"""
Excel Template Generator for Vsbvibe
Generates clean, validated Excel templates for content preparation
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from .utils import ensure_directory, save_json, load_json, log_activity

class TemplateGenerator:
    def __init__(self, project_manager):
        self.project_manager = project_manager
    
    def generate_templates(self) -> Dict[str, Any]:
        """Generate Excel templates based on plan configuration"""
        
        project_path = self.project_manager.get_current_project_path()
        if not project_path:
            raise ValueError("No project loaded")
        
        # Load plan and project config
        plan = self._load_plan()
        project_config = self.project_manager.get_project_config()
        
        if not plan or not project_config:
            raise ValueError("Missing plan or project configuration")
        
        # Ensure content directory structure
        content_path = os.path.join(project_path, "content")
        ensure_directory(content_path)
        ensure_directory(os.path.join(content_path, "images"))
        ensure_directory(os.path.join(content_path, "samples"))
        
        results = {
            "files_created": [],
            "files_updated": [],
            "templates_generated": 0
        }
        
        # Generate products template if needed
        if plan.get("entities", {}).get("products", False):
            products_result = self._generate_products_template(content_path)
            results["files_created"].extend(products_result["files_created"])
            results["templates_generated"] += 1
        
        # Generate pages template if brochure pages exist
        brochure_pages = self._get_brochure_pages(plan)
        if brochure_pages:
            pages_result = self._generate_pages_template(content_path, brochure_pages)
            results["files_created"].extend(pages_result["files_created"])
            results["templates_generated"] += 1
        
        # Generate documentation
        docs_result = self._generate_documentation(content_path, plan)
        results["files_created"].extend(docs_result["files_created"])
        
        # Log template generation
        self._log_template_generation(results)
        
        # Update diff summary
        self._update_diff_summary(results)
        
        return results
    
    def _load_plan(self) -> Optional[Dict[str, Any]]:
        """Load plan.json safely"""
        project_path = self.project_manager.get_current_project_path()
        plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
        return load_json(plan_path)
    
    def _get_brochure_pages(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get brochure pages from plan (non-ecommerce pages)"""
        pages = plan.get("pages", [])
        brochure_pages = []
        
        for page in pages:
            page_type = page.get("type", "")
            # Exclude ecommerce-specific pages
            if page_type not in ["product_list", "product_detail", "cart", "checkout"]:
                brochure_pages.append(page)
        
        return brochure_pages
    
    def _generate_products_template(self, content_path: str) -> Dict[str, Any]:
        """Generate products.xlsx template with examples and validation"""
        
        # Define columns with validation rules
        columns = [
            "title",           # Required
            "slug",            # Required, URL-safe
            "price",           # Required, numeric
            "description",     # Optional
            "sku",             # Optional
            "category",        # Optional
            "tags",            # Optional, comma-separated
            "image_main",      # Optional, filename or URL
            "image_extra",     # Optional, comma-separated filenames/URLs
            "image_alt_text"   # Optional, for accessibility
        ]
        
        # Create example data with validation comments
        example_data = {
            "title": [
                "Premium Wireless Headphones",
                "Organic Cotton T-Shirt",
                "Smart Home Security Camera"
            ],
            "slug": [
                "premium-wireless-headphones",  # URL-safe: lowercase, hyphens
                "organic-cotton-tshirt",
                "smart-security-camera"
            ],
            "price": [
                299.99,  # Numeric format
                49.95,
                179.00
            ],
            "description": [
                "High-quality wireless headphones with noise cancellation and 30-hour battery life.",
                "100% organic cotton t-shirt, sustainably sourced and ethically manufactured.",
                "AI-powered security camera with night vision and mobile alerts."
            ],
            "sku": [
                "WH-001",
                "TS-ORG-M",
                "CAM-SEC-01"
            ],
            "category": [
                "Electronics",
                "Clothing",
                "Home Security"
            ],
            "tags": [
                "wireless, audio, premium, noise-cancelling",
                "organic, cotton, sustainable, clothing",
                "security, smart-home, AI, camera"
            ],
            "image_main": [
                "premium-wireless-headphones.jpg",  # Matches slug
                "organic-cotton-tshirt_main.png",   # Alternative format
                "https://example.com/camera.jpg"    # Remote URL example
            ],
            "image_extra": [
                "premium-wireless-headphones_1.jpg, premium-wireless-headphones_2.jpg",
                "organic-cotton-tshirt_1.jpg, organic-cotton-tshirt_2.jpg",
                "smart-security-camera-box.jpg"
            ],
            "image_alt_text": [
                "Premium wireless headphones in black with carrying case",
                "Organic cotton t-shirt in natural color on model",
                "Smart security camera mounted on wall"
            ]
        }
        
        # Create DataFrame
        df = pd.DataFrame(example_data)
        
        # Save Excel file
        products_path = os.path.join(content_path, "products.xlsx")
        
        with pd.ExcelWriter(products_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='products', index=False)
            
            # Add validation comments to header row
            worksheet = writer.sheets['products']
            
            # Add comments to required columns
            worksheet['A1'].comment = "Required: Product display name"
            worksheet['B1'].comment = "Required: URL-safe identifier (lowercase, hyphens only)"
            worksheet['C1'].comment = "Required: Numeric price (e.g., 99.99)"
            worksheet['H1'].comment = "Image filename matching slug or full URL"
            worksheet['I1'].comment = "Additional images: comma-separated filenames"
            worksheet['J1'].comment = "Accessibility: describe images for screen readers"
        
        # Create CSV sample
        sample_path = os.path.join(content_path, "samples", "products_sample.csv")
        df.to_csv(sample_path, index=False)
        
        return {
            "files_created": [
                "content/products.xlsx",
                "content/samples/products_sample.csv"
            ]
        }
    
    def _generate_pages_template(self, content_path: str, brochure_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate pages.xlsx template for brochure content"""
        
        # Define columns
        columns = [
            "slug",              # Required, URL-safe
            "title",             # Required, page title
            "hero_headline",     # Optional, main headline
            "hero_subtitle",     # Optional, subtitle
            "body_markdown",     # Optional, main content in markdown
            "hero_image"         # Optional, hero image filename/URL
        ]
        
        # Create example data based on planned pages
        example_data = {
            "slug": [],
            "title": [],
            "hero_headline": [],
            "hero_subtitle": [],
            "body_markdown": [],
            "hero_image": []
        }
        
        # Add examples for first few brochure pages
        for i, page in enumerate(brochure_pages[:3]):
            page_name = page.get("name", f"Page {i+1}")
            page_slug = page.get("slug", f"/page-{i+1}").lstrip("/")
            
            if page_name.lower() == "about":
                example_data["slug"].append("about")
                example_data["title"].append("About Us")
                example_data["hero_headline"].append("Our Story")
                example_data["hero_subtitle"].append("Building excellence since day one")
                example_data["body_markdown"].append("## Who We Are\n\nWe are a passionate team dedicated to delivering exceptional results.\n\n### Our Mission\n\nTo provide outstanding service and innovative solutions.\n\n### Our Values\n\n- **Quality**: We never compromise on excellence\n- **Innovation**: We embrace new ideas and technologies\n- **Integrity**: We do business with honesty and transparency")
                example_data["hero_image"].append("about-hero.jpg")
            
            elif page_name.lower() == "contact":
                example_data["slug"].append("contact")
                example_data["title"].append("Contact Us")
                example_data["hero_headline"].append("Get In Touch")
                example_data["hero_subtitle"].append("We'd love to hear from you")
                example_data["body_markdown"].append("## Contact Information\n\n**Address:**\n123 Business Street\nCity, State 12345\n\n**Phone:** (555) 123-4567\n\n**Email:** hello@company.com\n\n**Business Hours:**\nMonday - Friday: 9:00 AM - 6:00 PM\nSaturday: 10:00 AM - 4:00 PM\nSunday: Closed")
                example_data["hero_image"].append("contact-hero.jpg")
            
            else:
                example_data["slug"].append(page_slug)
                example_data["title"].append(page_name)
                example_data["hero_headline"].append(f"Welcome to {page_name}")
                example_data["hero_subtitle"].append(f"Discover what {page_name.lower()} has to offer")
                example_data["body_markdown"].append(f"## {page_name}\n\nThis is the main content for the {page_name.lower()} page.\n\n### Key Features\n\n- Feature one\n- Feature two\n- Feature three\n\n### Learn More\n\nContact us to learn more about our {page_name.lower()} offerings.")
                example_data["hero_image"].append(f"{page_slug}-hero.jpg")
        
        # Create DataFrame
        df = pd.DataFrame(example_data)
        
        # Save Excel file
        pages_path = os.path.join(content_path, "pages.xlsx")
        
        with pd.ExcelWriter(pages_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='pages', index=False)
            
            # Add validation comments
            worksheet = writer.sheets['pages']
            worksheet['A1'].comment = "Required: URL-safe page identifier (no spaces, special chars)"
            worksheet['B1'].comment = "Required: Page title for navigation and SEO"
            worksheet['C1'].comment = "Main headline displayed prominently on page"
            worksheet['E1'].comment = "Markdown content: use ## for headings, **bold**, *italic*"
            worksheet['F1'].comment = "Hero image filename (matches slug) or full URL"
        
        # Create CSV sample
        sample_path = os.path.join(content_path, "samples", "pages_sample.csv")
        df.to_csv(sample_path, index=False)
        
        return {
            "files_created": [
                "content/pages.xlsx",
                "content/samples/pages_sample.csv"
            ]
        }
    
    def _generate_documentation(self, content_path: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive import documentation"""
        
        site_mode = plan.get("site_mode", "brochure")
        has_products = plan.get("entities", {}).get("products", False)
        
        readme_content = f"""# Content Import Guide

## Overview

This guide explains how to prepare content for your {site_mode} website using Excel templates.

## File Structure

```
content/
├── products.xlsx      # Product catalog (if e-commerce)
├── pages.xlsx         # Page content (if brochure pages)
├── images/           # Local image files
├── samples/          # Example CSV files
└── README_import.md  # This guide
```

## Templates Generated

"""
        
        if has_products:
            readme_content += """### Products Template (products.xlsx)

**Required Columns:**
- `title*`: Product display name
- `slug*`: URL-safe identifier (lowercase, hyphens only)
- `price*`: Numeric price (e.g., 99.99)

**Optional Columns:**
- `description`: Product description
- `sku`: Stock keeping unit
- `category`: Product category
- `tags`: Comma-separated tags
- `image_main`: Primary product image
- `image_extra`: Additional images (comma-separated)
- `image_alt_text`: Accessibility descriptions

**Validation Rules:**
- Slugs must be unique and URL-safe (no spaces, special characters)
- Prices must be numeric (use decimal format: 99.99)
- Image filenames should match slug when possible

"""
        
        brochure_pages = self._get_brochure_pages(plan)
        if brochure_pages:
            readme_content += """### Pages Template (pages.xlsx)

**Required Columns:**
- `slug*`: URL-safe page identifier
- `title*`: Page title for navigation and SEO

**Optional Columns:**
- `hero_headline`: Main page headline
- `hero_subtitle`: Supporting subtitle
- `body_markdown`: Main content in Markdown format
- `hero_image`: Hero section image

**Markdown Support:**
- Use `##` for headings
- Use `**bold**` and `*italic*` for emphasis
- Use `-` for bullet lists
- Use `[link text](URL)` for links

"""
        
        readme_content += """## Image Auto-Mapping

The system automatically maps images using these rules:

### Primary Images
- `<slug>.jpg/png/webp` → Primary image
- `<slug>_main.jpg/png/webp` → Primary image (alternative)

### Additional Images
- `<slug>_1.jpg`, `<slug>_2.jpg` → Extra images (numbered)
- `<slug>-1.jpg`, `<slug>-2.jpg` → Extra images (hyphenated)

### Image Sources
- **Local**: Place files in `content/images/` folder
- **Remote**: Use full URLs (https://example.com/image.jpg)
- **Stock**: System will suggest stock photos if images missing

## Naming Best Practices

1. **Match Filenames to Slugs**: Use the same identifier
   - Product slug: `wireless-headphones`
   - Image: `wireless-headphones.jpg`

2. **Use Descriptive Alt Text**: Essential for accessibility
   - Good: "Wireless headphones in black with carrying case"
   - Bad: "Image1" or "Headphones"

3. **Consistent Naming**: Use hyphens, not underscores in slugs
   - Good: `premium-coffee-beans`
   - Bad: `premium_coffee_beans` or `Premium Coffee Beans`

## Step 5 Import Process

### Dry Run (Preview)
1. Upload your completed Excel files
2. System validates data and shows preview table
3. Review status indicators:
   - ✅ Valid entries
   - ⚠️ Warnings (missing images, etc.)
   - ❌ Errors (duplicate slugs, invalid data)

### Apply Changes
1. Fix any validation errors
2. Click "Apply Import" to update site
3. System creates backup before applying changes

### Undo Support
- Previous data backed up automatically
- "Undo Last Import" restores previous state
- Change history maintained in logs

## Validation & Quick Fixes

### Common Issues
- **Duplicate Slugs**: Each slug must be unique
- **Invalid Prices**: Must be numeric (99.99, not $99.99)
- **Missing Images**: System will suggest alternatives
- **Non-URL-Safe Slugs**: Use lowercase letters, numbers, hyphens only

### Auto-Fixes Available
- Slug sanitization (spaces → hyphens, remove special chars)
- Price cleaning (remove currency symbols)
- Image path normalization
- Markdown formatting cleanup

## Support

If you encounter issues:
1. Check the validation messages in Step 5
2. Review examples in `content/samples/`
3. Ensure required columns are filled
4. Verify image files exist in `content/images/`

For technical issues, check Admin → Errors panel for detailed error reports.
"""
        
        # Save documentation
        readme_path = os.path.join(content_path, "README_import.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return {
            "files_created": ["content/README_import.md"]
        }
    
    def _get_brochure_pages(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get brochure pages from plan (reused from above)"""
        pages = plan.get("pages", [])
        brochure_pages = []
        
        for page in pages:
            page_type = page.get("type", "")
            if page_type not in ["product_list", "product_detail", "cart", "checkout"]:
                brochure_pages.append(page)
        
        return brochure_pages
    
    def _log_template_generation(self, results: Dict[str, Any]):
        """Log template generation to templates.log"""
        
        project_path = self.project_manager.get_current_project_path()
        logs_path = os.path.join(project_path, "_vsbvibe", "logs")
        ensure_directory(logs_path)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": "template_generation",
            "templates_count": results["templates_generated"],
            "files_created": len(results["files_created"]),
            "success": True
        }
        
        # Append to templates.log
        templates_log_path = os.path.join(logs_path, "templates.log")
        with open(templates_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Log activity
        log_activity(
            project_path,
            "templates_generated",
            f"Generated {results['templates_generated']} Excel templates"
        )
    
    def _update_diff_summary(self, results: Dict[str, Any]):
        """Update diff summary with template generation"""
        
        project_path = self.project_manager.get_current_project_path()
        diff_path = os.path.join(project_path, "_vsbvibe", "diff_summary.json")
        
        # Load existing diff summary
        diff_summary = load_json(diff_path) or {
            "timestamp": datetime.now().isoformat(),
            "operation": "template_generation",
            "files_created": [],
            "files_updated": [],
            "summary": ""
        }
        
        # Update with new files
        diff_summary["files_created"].extend(results["files_created"])
        diff_summary["files_updated"].extend(results["files_updated"])
        diff_summary["timestamp"] = datetime.now().isoformat()
        diff_summary["operation"] = "template_generation"
        diff_summary["summary"] = f"Generated {results['templates_generated']} Excel templates with documentation"
        
        # Save updated diff summary
        save_json(diff_path, diff_summary)