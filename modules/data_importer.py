"""
Data Import & Image Auto-Mapping System for Vsbvibe
Handles Excel import with dry-run, apply, and undo functionality
"""

import os
import json
import pandas as pd
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from .utils import ensure_directory, save_json, load_json, log_activity
from site.core.errors import safe_page, safe_component
from site.core.telemetry import log_event

class DataImporter:
    def __init__(self, project_manager):
        self.project_manager = project_manager
        self.project_path = project_manager.get_current_project_path()
        self.content_path = os.path.join(self.project_path, "content")
        self.images_path = os.path.join(self.content_path, "images")
        
    @safe_component
    def dry_run_import(self, products_file=None, pages_file=None) -> Dict[str, Any]:
        """Perform dry-run validation and preview without writing content store"""
        
        log_event("dry_run_start", {"has_products": products_file is not None, "has_pages": pages_file is not None})
        
        results = {
            "products": {"rows": [], "issues": [], "counts": {"valid": 0, "warnings": 0, "errors": 0}},
            "pages": {"rows": [], "issues": [], "counts": {"valid": 0, "warnings": 0, "errors": 0}},
            "global_issues": [],
            "image_mapping": {},
            "summary": {}
        }
        
        try:
            # Load plan to check what's enabled
            plan = self._load_plan()
            if not plan:
                results["global_issues"].append("Plan not found - cannot validate against requirements")
                return results
            
            # Validate products if provided and enabled
            if products_file and plan.get("entities", {}).get("products", False):
                products_results = self._validate_products_excel(products_file)
                results["products"] = products_results
            
            # Validate pages if provided
            if pages_file:
                pages_results = self._validate_pages_excel(pages_file)
                results["pages"] = pages_results
            
            # Check for duplicate slugs across products and pages
            all_slugs = []
            all_slugs.extend([row["slug"] for row in results["products"]["rows"] if row.get("slug")])
            all_slugs.extend([row["slug"] for row in results["pages"]["rows"] if row.get("slug")])
            
            duplicate_slugs = self._find_duplicates(all_slugs)
            if duplicate_slugs:
                results["global_issues"].append(f"Duplicate slugs found: {', '.join(duplicate_slugs)}")
            
            # Generate image mapping
            results["image_mapping"] = self._generate_image_mapping(results["products"]["rows"] + results["pages"]["rows"])
            
            # Create summary
            total_rows = len(results["products"]["rows"]) + len(results["pages"]["rows"])
            total_issues = len(results["products"]["issues"]) + len(results["pages"]["issues"]) + len(results["global_issues"])
            
            results["summary"] = {
                "total_rows": total_rows,
                "total_issues": total_issues,
                "products_count": len(results["products"]["rows"]),
                "pages_count": len(results["pages"]["rows"]),
                "ready_to_apply": total_issues == 0
            }
            
            # Write issues.csv if there are validation failures
            if total_issues > 0:
                self._write_issues_csv(results)
            
            log_event("dry_run_complete", results["summary"])
            
            return results
            
        except Exception as e:
            from site.core.errors import error_reporter
            error_id = error_reporter.capture_error(e, {
                "module": "data_importer",
                "function": "dry_run_import",
                "has_products": products_file is not None,
                "has_pages": pages_file is not None
            })
            
            results["global_issues"].append(f"Import validation failed: {str(e)} (Error ID: {error_id})")
            return results
    
    @safe_component
    def apply_import(self, dry_run_results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply validated import to content store with backup"""
        
        log_event("apply_import_start", {"total_rows": dry_run_results["summary"]["total_rows"]})
        
        try:
            # Create backup snapshot
            snapshot_path = self._create_content_snapshot()
            
            # Load current content store
            content_store = self._load_content_store()
            
            # Apply products
            products_applied = 0
            if dry_run_results["products"]["rows"]:
                content_store["products"] = []
                for row in dry_run_results["products"]["rows"]:
                    if row.get("status") == "✅":  # Only apply valid rows
                        product_data = self._convert_row_to_product(row)
                        content_store["products"].append(product_data)
                        products_applied += 1
            
            # Apply pages
            pages_applied = 0
            if dry_run_results["pages"]["rows"]:
                if "pages" not in content_store:
                    content_store["pages"] = {}
                
                for row in dry_run_results["pages"]["rows"]:
                    if row.get("status") == "✅":  # Only apply valid rows
                        page_data = self._convert_row_to_page(row)
                        content_store["pages"][row["slug"]] = page_data
                        pages_applied += 1
            
            # Update content store metadata
            content_store["updated_at"] = datetime.now().isoformat()
            content_store["last_import"] = {
                "timestamp": datetime.now().isoformat(),
                "products_count": products_applied,
                "pages_count": pages_applied,
                "snapshot_path": snapshot_path
            }
            
            # Save content store
            self._save_content_store(content_store)
            
            # Save image mapping
            mapping_path = os.path.join(self.project_path, "_vsbvibe", "mapping", "image_map.json")
            ensure_directory(os.path.dirname(mapping_path))
            save_json(mapping_path, dry_run_results["image_mapping"])
            
            # Generate platform-specific exports
            self._generate_platform_exports(content_store)
            
            # Log import details
            self._log_import_completion(products_applied, pages_applied, snapshot_path)
            
            # Update diff summary
            self._update_diff_summary_import(products_applied, pages_applied)
            
            log_event("apply_import_complete", {
                "products_applied": products_applied,
                "pages_applied": pages_applied,
                "snapshot_created": snapshot_path
            })
            
            return {
                "success": True,
                "products_applied": products_applied,
                "pages_applied": pages_applied,
                "snapshot_path": snapshot_path,
                "message": f"Import successful: {products_applied} products, {pages_applied} pages"
            }
            
        except Exception as e:
            from site.core.errors import error_reporter
            error_id = error_reporter.capture_error(e, {
                "module": "data_importer",
                "function": "apply_import",
                "dry_run_summary": dry_run_results["summary"]
            })
            
            return {
                "success": False,
                "error": str(e),
                "error_id": error_id,
                "message": f"Import failed: {str(e)}"
            }
    
    @safe_component
    def undo_last_import(self) -> Dict[str, Any]:
        """Restore previous content store from snapshot"""
        
        log_event("undo_import_start")
        
        try:
            # Load current content store to get snapshot path
            content_store = self._load_content_store()
            last_import = content_store.get("last_import", {})
            snapshot_path = last_import.get("snapshot_path")
            
            if not snapshot_path or not os.path.exists(snapshot_path):
                return {
                    "success": False,
                    "message": "No snapshot available for undo"
                }
            
            # Restore from snapshot
            shutil.copy2(snapshot_path, self._get_content_store_path())
            
            # Log undo operation
            import_log_path = os.path.join(self.project_path, "_vsbvibe", "logs", "import.log")
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation": "undo",
                "snapshot_restored": snapshot_path,
                "success": True
            }
            
            with open(import_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            log_event("undo_import_complete", {"snapshot_restored": snapshot_path})
            
            return {
                "success": True,
                "message": "Import successfully undone",
                "snapshot_restored": snapshot_path
            }
            
        except Exception as e:
            from site.core.errors import error_reporter
            error_id = error_reporter.capture_error(e, {
                "module": "data_importer",
                "function": "undo_last_import"
            })
            
            return {
                "success": False,
                "error": str(e),
                "error_id": error_id,
                "message": f"Undo failed: {str(e)}"
            }
    
    @safe_component
    def _validate_products_excel(self, products_file) -> Dict[str, Any]:
        """Validate products Excel file and return row-wise results"""
        
        try:
            df = pd.read_excel(products_file)
            
            # Check required columns
            required_cols = ["title", "slug", "price"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return {
                    "rows": [],
                    "issues": [f"Missing required columns: {', '.join(missing_cols)}"],
                    "counts": {"valid": 0, "warnings": 0, "errors": 1}
                }
            
            rows = []
            issues = []
            counts = {"valid": 0, "warnings": 0, "errors": 0}
            
            for idx, row in df.iterrows():
                row_result = self._validate_product_row(row, idx)
                rows.append(row_result)
                
                if row_result["status"] == "✅":
                    counts["valid"] += 1
                elif row_result["status"] in ["🟠", "🔵", "🟣"]:
                    counts["warnings"] += 1
                else:
                    counts["errors"] += 1
                    issues.append(f"Row {idx + 2}: {row_result['message']}")
            
            return {
                "rows": rows,
                "issues": issues,
                "counts": counts
            }
            
        except Exception as e:
            return {
                "rows": [],
                "issues": [f"Cannot read Excel file: {str(e)}"],
                "counts": {"valid": 0, "warnings": 0, "errors": 1}
            }
    
    @safe_component
    def _validate_pages_excel(self, pages_file) -> Dict[str, Any]:
        """Validate pages Excel file and return row-wise results"""
        
        try:
            df = pd.read_excel(pages_file)
            
            # Check required columns
            required_cols = ["slug", "title"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return {
                    "rows": [],
                    "issues": [f"Missing required columns: {', '.join(missing_cols)}"],
                    "counts": {"valid": 0, "warnings": 0, "errors": 1}
                }
            
            rows = []
            issues = []
            counts = {"valid": 0, "warnings": 0, "errors": 0}
            
            for idx, row in df.iterrows():
                row_result = self._validate_page_row(row, idx)
                rows.append(row_result)
                
                if row_result["status"] == "✅":
                    counts["valid"] += 1
                elif row_result["status"] in ["🟠", "🔵"]:
                    counts["warnings"] += 1
                else:
                    counts["errors"] += 1
                    issues.append(f"Row {idx + 2}: {row_result['message']}")
            
            return {
                "rows": rows,
                "issues": issues,
                "counts": counts
            }
            
        except Exception as e:
            return {
                "rows": [],
                "issues": [f"Cannot read Excel file: {str(e)}"],
                "counts": {"valid": 0, "warnings": 0, "errors": 1}
            }
    
    @safe_component
    def _validate_product_row(self, row: pd.Series, idx: int) -> Dict[str, Any]:
        """Validate individual product row with image auto-mapping"""
        
        # Extract basic fields
        title = str(row.get("title", "")).strip()
        slug = str(row.get("slug", "")).strip()
        price = row.get("price", "")
        
        # Validate required fields
        if not title:
            return {"status": "🔴", "message": "Missing title", "slug": slug, "title": title, "row": idx + 2}
        
        if not slug:
            return {"status": "🔴", "message": "Missing slug", "slug": slug, "title": title, "row": idx + 2}
        
        if not self._is_url_safe(slug):
            return {"status": "🔴", "message": "Slug not URL-safe", "slug": slug, "title": title, "row": idx + 2}
        
        # Validate price
        try:
            price_num = float(str(price).replace("$", "").replace(",", ""))
            if price_num < 0:
                return {"status": "🔴", "message": "Price cannot be negative", "slug": slug, "title": title, "row": idx + 2}
        except (ValueError, TypeError):
            return {"status": "🔴", "message": "Price must be numeric", "slug": slug, "title": title, "row": idx + 2}
        
        # Image auto-mapping
        image_main = str(row.get("image_main", "")).strip()
        image_results = self._map_images_for_slug(slug, image_main)
        
        # Determine status based on image mapping
        if image_results["main_image"]:
            if image_results["main_image"].startswith("http"):
                status = "🔵"  # External URL
                message = "External image URL"
            elif image_results["confidence"] == "exact":
                status = "✅"  # Perfect match
                message = "All fields valid"
            elif image_results["confidence"] == "fuzzy":
                status = "🟠"  # Fuzzy match
                message = f"Fuzzy image match: {image_results['main_image']}"
            else:
                status = "✅"  # Manual image specified
                message = "Manual image specified"
        else:
            status = "🟠"  # Missing image
            message = "No main image found"
        
        # Check for multiple main candidates
        if len(image_results["main_candidates"]) > 1:
            status = "🟣"  # Multiple mains
            message = f"Multiple main images found: {', '.join(image_results['main_candidates'])}"
        
        return {
            "status": status,
            "message": message,
            "slug": slug,
            "title": title,
            "price": price_num,
            "row": idx + 2,
            "image_main": image_results["main_image"],
            "image_extras": image_results["extra_images"],
            "image_candidates": image_results["main_candidates"],
            "data": row.to_dict()
        }
    
    @safe_component
    def _validate_page_row(self, row: pd.Series, idx: int) -> Dict[str, Any]:
        """Validate individual page row with image auto-mapping"""
        
        # Extract basic fields
        title = str(row.get("title", "")).strip()
        slug = str(row.get("slug", "")).strip()
        
        # Validate required fields
        if not title:
            return {"status": "🔴", "message": "Missing title", "slug": slug, "title": title, "row": idx + 2}
        
        if not slug:
            return {"status": "🔴", "message": "Missing slug", "slug": slug, "title": title, "row": idx + 2}
        
        if not self._is_url_safe(slug):
            return {"status": "🔴", "message": "Slug not URL-safe", "slug": slug, "title": title, "row": idx + 2}
        
        # Image auto-mapping for hero image
        hero_image = str(row.get("hero_image", "")).strip()
        image_results = self._map_images_for_slug(slug, hero_image)
        
        # Determine status
        if image_results["main_image"]:
            if image_results["main_image"].startswith("http"):
                status = "🔵"  # External URL
                message = "External hero image"
            else:
                status = "✅"  # Local image found
                message = "All fields valid"
        else:
            status = "✅"  # No image required for pages
            message = "Valid (no hero image)"
        
        return {
            "status": status,
            "message": message,
            "slug": slug,
            "title": title,
            "row": idx + 2,
            "hero_image": image_results["main_image"],
            "data": row.to_dict()
        }
    
    @safe_component
    def _map_images_for_slug(self, slug: str, specified_image: str = "") -> Dict[str, Any]:
        """Auto-map images for a given slug using naming conventions"""
        
        # If external URL specified, use as-is
        if specified_image and specified_image.startswith("http"):
            return {
                "main_image": specified_image,
                "extra_images": [],
                "main_candidates": [specified_image],
                "confidence": "external"
            }
        
        # If local file specified, check if it exists
        if specified_image:
            specified_path = os.path.join(self.images_path, specified_image)
            if os.path.exists(specified_path):
                return {
                    "main_image": specified_image,
                    "extra_images": self._find_extra_images(slug),
                    "main_candidates": [specified_image],
                    "confidence": "manual"
                }
        
        # Auto-detect based on slug
        if not os.path.exists(self.images_path):
            return {
                "main_image": None,
                "extra_images": [],
                "main_candidates": [],
                "confidence": "none"
            }
        
        # Find main image candidates
        main_candidates = []
        extra_images = []
        
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        image_files = []
        
        for ext in image_extensions:
            # Exact matches
            exact_file = f"{slug}{ext}"
            exact_path = os.path.join(self.images_path, exact_file)
            if os.path.exists(exact_path):
                main_candidates.append(exact_file)
            
            # Main variants
            main_file = f"{slug}_main{ext}"
            main_path = os.path.join(self.images_path, main_file)
            if os.path.exists(main_path):
                main_candidates.append(main_file)
        
        # Find extra images
        extra_images = self._find_extra_images(slug)
        
        # Fuzzy matching if no exact matches
        if not main_candidates:
            main_candidates = self._fuzzy_match_images(slug)
        
        # Select best main image
        main_image = None
        confidence = "none"
        
        if main_candidates:
            # Prefer _main variants, then exact matches
            main_variants = [img for img in main_candidates if "_main" in img]
            if main_variants:
                main_image = main_variants[0]
                confidence = "exact"
            else:
                main_image = main_candidates[0]
                confidence = "exact" if len(main_candidates) == 1 else "fuzzy"
        
        return {
            "main_image": main_image,
            "extra_images": extra_images,
            "main_candidates": main_candidates,
            "confidence": confidence
        }
    
    @safe_component
    def _find_extra_images(self, slug: str) -> List[str]:
        """Find extra images for a slug using naming conventions"""
        
        if not os.path.exists(self.images_path):
            return []
        
        extra_images = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        
        # Pattern: slug_1, slug_2, slug-1, slug-2, etc.
        for i in range(1, 10):  # Check up to 9 extra images
            for separator in ['_', '-']:
                for ext in image_extensions:
                    extra_file = f"{slug}{separator}{i}{ext}"
                    extra_path = os.path.join(self.images_path, extra_file)
                    if os.path.exists(extra_path):
                        extra_images.append(extra_file)
        
        return extra_images
    
    @safe_component
    def _fuzzy_match_images(self, slug: str) -> List[str]:
        """Fuzzy match images using case-insensitive begins-with"""
        
        if not os.path.exists(self.images_path):
            return []
        
        candidates = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        
        try:
            for filename in os.listdir(self.images_path):
                file_lower = filename.lower()
                slug_lower = slug.lower()
                
                # Check if filename starts with slug (case-insensitive)
                if file_lower.startswith(slug_lower):
                    # Verify it's an image file
                    if any(file_lower.endswith(ext) for ext in image_extensions):
                        candidates.append(filename)
        except:
            pass
        
        return candidates
    
    @safe_component
    def _is_url_safe(self, slug: str) -> bool:
        """Check if slug is URL-safe"""
        import re
        # Allow alphanumeric, hyphens, underscores, forward slashes
        pattern = r'^[a-zA-Z0-9\-_/]*$'
        return bool(re.match(pattern, slug)) and slug == slug.lower()
    
    @safe_component
    def _find_duplicates(self, items: List[str]) -> List[str]:
        """Find duplicate items in list"""
        seen = set()
        duplicates = set()
        
        for item in items:
            if item in seen:
                duplicates.add(item)
            else:
                seen.add(item)
        
        return list(duplicates)
    
    @safe_component
    def _generate_image_mapping(self, all_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive image mapping for all content"""
        
        mapping = {}
        
        for row in all_rows:
            slug = row.get("slug")
            if not slug:
                continue
            
            mapping[slug] = {
                "main_image": row.get("image_main"),
                "extra_images": row.get("image_extras", []),
                "alt_text": row.get("data", {}).get("image_alt_text", ""),
                "confidence": row.get("confidence", "unknown"),
                "candidates": row.get("image_candidates", [])
            }
        
        return mapping
    
    @safe_component
    def _write_issues_csv(self, results: Dict[str, Any]):
        """Write validation issues to CSV for user review"""
        
        issues_data = []
        
        # Add product issues
        for issue in results["products"]["issues"]:
            issues_data.append({
                "Type": "Products",
                "Issue": issue,
                "Severity": "Error",
                "Action": "Fix in products.xlsx"
            })
        
        # Add page issues
        for issue in results["pages"]["issues"]:
            issues_data.append({
                "Type": "Pages", 
                "Issue": issue,
                "Severity": "Error",
                "Action": "Fix in pages.xlsx"
            })
        
        # Add global issues
        for issue in results["global_issues"]:
            issues_data.append({
                "Type": "Global",
                "Issue": issue,
                "Severity": "Error",
                "Action": "Review and fix"
            })
        
        # Add row-level warnings
        for row in results["products"]["rows"] + results["pages"]["rows"]:
            if row["status"] in ["🟠", "🟣"]:
                issues_data.append({
                    "Type": "Products" if "price" in row.get("data", {}) else "Pages",
                    "Issue": f"Row {row['row']}: {row['message']}",
                    "Severity": "Warning",
                    "Action": "Review and confirm"
                })
        
        if issues_data:
            df = pd.DataFrame(issues_data)
            issues_path = os.path.join(self.project_path, "_vsbvibe", "issues.csv")
            df.to_csv(issues_path, index=False)
    
    @safe_component
    def _create_content_snapshot(self) -> str:
        """Create backup snapshot of current content store"""
        
        snapshots_dir = os.path.join(self.project_path, "_vsbvibe", "snapshots")
        ensure_directory(snapshots_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_filename = f"content_before_{timestamp}.json"
        snapshot_path = os.path.join(snapshots_dir, snapshot_filename)
        
        # Copy current content store
        content_store_path = self._get_content_store_path()
        if os.path.exists(content_store_path):
            shutil.copy2(content_store_path, snapshot_path)
        else:
            # Create empty snapshot
            empty_store = {
                "products": [],
                "pages": {},
                "global": {},
                "created_at": datetime.now().isoformat()
            }
            save_json(snapshot_path, empty_store)
        
        return snapshot_path
    
    @safe_component
    def _load_content_store(self) -> Dict[str, Any]:
        """Load current content store"""
        
        content_store_path = self._get_content_store_path()
        content_store = load_json(content_store_path)
        
        if not content_store:
            # Create default content store
            content_store = {
                "products": [],
                "pages": {},
                "global": {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        return content_store
    
    @safe_component
    def _save_content_store(self, content_store: Dict[str, Any]):
        """Save content store to file"""
        
        content_store_path = self._get_content_store_path()
        save_json(content_store_path, content_store)
    
    @safe_component
    def _get_content_store_path(self) -> str:
        """Get path to content store file"""
        return os.path.join(self.project_path, "_vsbvibe", "content_store.json")
    
    @safe_component
    def _convert_row_to_product(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Convert validated row to product data structure"""
        
        data = row.get("data", {})
        
        return {
            "id": row["slug"],
            "title": row["title"],
            "slug": row["slug"],
            "price": row["price"],
            "description": str(data.get("description", "")).strip(),
            "sku": str(data.get("sku", "")).strip(),
            "category": str(data.get("category", "")).strip(),
            "tags": [tag.strip() for tag in str(data.get("tags", "")).split(",") if tag.strip()],
            "images": {
                "main": row.get("image_main", ""),
                "extras": row.get("image_extras", []),
                "alt_text": str(data.get("image_alt_text", "")).strip()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    @safe_component
    def _convert_row_to_page(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Convert validated row to page data structure"""
        
        data = row.get("data", {})
        
        return {
            "slug": row["slug"],
            "title": row["title"],
            "hero": {
                "headline": str(data.get("hero_headline", "")).strip(),
                "subtitle": str(data.get("hero_subtitle", "")).strip(),
                "image": row.get("hero_image", "")
            },
            "content": {
                "markdown": str(data.get("body_markdown", "")).strip()
            },
            "seo": {
                "title": row["title"],
                "description": str(data.get("hero_subtitle", "")).strip()[:160]
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    @safe_component
    def _generate_platform_exports(self, content_store: Dict[str, Any]):
        """Generate platform-specific data exports"""
        
        plan = self._load_plan()
        if not plan:
            return
        
        platform_target = plan.get("platform_target", "")
        
        if platform_target == "htmljs":
            # Export JSON files for static site
            output_path = os.path.join(self.project_path, "output", self.project_manager.get_project_config().get("project_name", "project").lower().replace(" ", "-"), "htmljs", "data")
            ensure_directory(output_path)
            
            # Export products.json
            if content_store.get("products"):
                products_json_path = os.path.join(output_path, "products.json")
                save_json(products_json_path, content_store["products"])
            
            # Export pages.json
            if content_store.get("pages"):
                pages_json_path = os.path.join(output_path, "pages.json")
                save_json(pages_json_path, content_store["pages"])
        
        # For streamlit_site, no export needed - pages read directly from content store
    
    @safe_component
    def _load_plan(self) -> Optional[Dict[str, Any]]:
        """Load plan.json safely"""
        plan_path = os.path.join(self.project_path, "_vsbvibe", "plan.json")
        return load_json(plan_path)
    
    @safe_component
    def _log_import_completion(self, products_count: int, pages_count: int, snapshot_path: str):
        """Log import completion to import.log"""
        
        logs_dir = os.path.join(self.project_path, "_vsbvibe", "logs")
        ensure_directory(logs_dir)
        
        import_log_path = os.path.join(logs_dir, "import.log")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": "apply_import",
            "products_imported": products_count,
            "pages_imported": pages_count,
            "snapshot_created": snapshot_path,
            "success": True
        }
        
        with open(import_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Log activity
        log_activity(
            self.project_path,
            "import_completed",
            f"Imported {products_count} products, {pages_count} pages"
        )
    
    @safe_component
    def _update_diff_summary_import(self, products_count: int, pages_count: int):
        """Update diff summary with import details"""
        
        diff_path = os.path.join(self.project_path, "_vsbvibe", "diff_summary.json")
        diff_summary = load_json(diff_path) or {
            "timestamp": datetime.now().isoformat(),
            "operation": "data_import",
            "files_created": [],
            "files_updated": [],
            "summary": ""
        }
        
        # Update with import details
        files_updated = ["_vsbvibe/content_store.json"]
        
        if products_count > 0:
            files_updated.append("_vsbvibe/mapping/image_map.json")
        
        # Add platform-specific exports
        plan = self._load_plan()
        if plan and plan.get("platform_target") == "htmljs":
            if products_count > 0:
                files_updated.append("output/*/htmljs/data/products.json")
            if pages_count > 0:
                files_updated.append("output/*/htmljs/data/pages.json")
        
        diff_summary["files_updated"].extend(files_updated)
        diff_summary["timestamp"] = datetime.now().isoformat()
        diff_summary["operation"] = "data_import"
        diff_summary["summary"] = f"Imported {products_count} products, {pages_count} pages with image auto-mapping"
        
        save_json(diff_path, diff_summary)