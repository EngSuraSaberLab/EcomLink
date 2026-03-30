from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.utils import translation

django.setup()

from store.models import Category, Product, Slider

DOCS_DIR = BASE_DIR / "docs"
STATIC_DIR = BASE_DIR / "static"
MEDIA_DIR = BASE_DIR / "media"
BASE_PATH = "/EcomLink"
MOSTAQL_URL = "https://mostaql.com/u/I_am_Sura"

factory = RequestFactory()


def make_request(path: str, language_code: str):
    request = factory.get(path)
    request.LANGUAGE_CODE = language_code
    request.get_full_path = lambda: path
    request.user = SimpleNamespace(is_authenticated=False)
    request.session = {}
    return request


def make_common_context(language_code: str):
    return {
        "navbar_categories": list(Category.objects.order_by("order", "name")),
        "cart_item_count": 0,
        "static_export": True,
        "static_base_path": BASE_PATH,
        "showcase_contact_url": MOSTAQL_URL,
        "showcase_message_en": "This is a static showcase. Please contact me through my Mostaql account to start your project.",
        "showcase_message_ar": "هذا الموقع نسخة عرض ثابتة. يرجى التواصل معي عبر حسابي على مستقل لبدء مشروعك.",
        "showcase_button_en": "Open Mostaql",
        "showcase_button_ar": "فتح مستقل",
        "language_switch_en": f"{BASE_PATH}/",
        "language_switch_ar": f"{BASE_PATH}/ar/",
    }


def render(template_name: str, context: dict, path: str, language_code: str) -> str:
    request = make_request(path, language_code)
    payload = {**make_common_context(language_code), **context, "request": request}
    with translation.override(language_code):
        html = render_to_string(template_name, payload, request=request)
    return rewrite_html(html, language_code)


def rewrite_html(html: str, language_code: str) -> str:
    html = html.replace('/static/', f'{BASE_PATH}/assets/')
    html = html.replace('/media/', f'{BASE_PATH}/media/')

    if language_code == 'en':
        html = html.replace('href="/en/', f'href="{BASE_PATH}/')
        html = html.replace('action="/en/', f'action="{BASE_PATH}/')
        html = html.replace('href="/ar/', f'href="{BASE_PATH}/ar/')
        html = html.replace('action="/ar/', f'action="{BASE_PATH}/ar/')
        html = re.sub(r'((?:href|action)="|(?:href|action)=\')/(?!EcomLink/|https?:|mailto:|tel:|#)', r'\1' + BASE_PATH + '/', html)
    else:
        html = re.sub(r'((?:href|action)="|(?:href|action)=\')/(?!EcomLink/|https?:|mailto:|tel:|#)', r'\1' + BASE_PATH + '/ar/', html)

    html = html.replace(f'{BASE_PATH}/ar/i18n/', f'{BASE_PATH}/i18n/')
    html = html.replace(f'{BASE_PATH}/i18n/', '#')
    return html


def write_page(relative_path: str, html: str) -> None:
    destination = DOCS_DIR / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding='utf-8')


def export_language(language_code: str, prefix: str) -> None:
    products = list(Product.objects.select_related('author', 'category').order_by('-created_at'))
    categories = list(Category.objects.order_by('order', 'name'))
    sliders = list(Slider.objects.order_by('order', '-created_at'))

    root_prefix = f'{prefix}/' if prefix else ''
    lang_path = '/en/' if language_code == 'en' else '/'

    write_page(
        f'{root_prefix}index.html',
        render('index.html', {"products": products[:8], "sliders": sliders}, lang_path, language_code),
    )

    write_page(
        f'{root_prefix}category/index.html',
        render(
            'category.html',
            {"categories": categories, "products": products, "selected_category": None, "search_query": ""},
            f'{lang_path}category/',
            language_code,
        ),
    )

    for category in categories:
        category_products = [product for product in products if product.category_id == category.id]
        write_page(
            f'{root_prefix}category/{category.slug}/index.html',
            render(
                'category.html',
                {"categories": categories, "products": category_products, "selected_category": category, "search_query": ""},
                f'{lang_path}category/{category.slug}/',
                language_code,
            ),
        )

    for product in products:
        related_products = [item for item in products if item.category_id == product.category_id and item.id != product.id][:4]
        write_page(
            f'{root_prefix}product/{product.slug}/index.html',
            render(
                'product.html',
                {"product": product, "related_products": related_products},
                f'{lang_path}product/{product.slug}/',
                language_code,
            ),
        )

    write_page(
        f'{root_prefix}contact/index.html',
        render(
            'contact.html',
            {"categories": categories[:6], "featured_products": products[:3]},
            f'{lang_path}contact/',
            language_code,
        ),
    )

    write_page(
        f'{root_prefix}cart/index.html',
        render('cart.html', {"cart_items": [], "cart_total": 0}, f'{lang_path}cart/', language_code),
    )

    write_page(
        f'{root_prefix}checkout/index.html',
        render('checkout.html', {"cart_items": [], "cart_total": 0}, f'{lang_path}checkout/', language_code),
    )

    write_page(
        f'{root_prefix}checkout/complete/index.html',
        render('checkout-complete.html', {"latest_order": None}, f'{lang_path}checkout/complete/', language_code),
    )


def export_404() -> None:
    html = render(
        'category.html',
        {"categories": list(Category.objects.order_by('order', 'name')), "products": [], "selected_category": None, "search_query": ""},
        '/en/404/',
        'en',
    )
    html = html.replace('<h1 class="text-center text-secondary">Categories</h1>', '<h1 class="text-center text-secondary">Page Not Found</h1>')
    html = html.replace('No products in this category.', 'The page you are looking for is not available in this static showcase.')
    write_page('404.html', html)


def copy_assets() -> None:
    assets_dest = DOCS_DIR / 'assets'
    media_dest = DOCS_DIR / 'media'
    if assets_dest.exists():
        shutil.rmtree(assets_dest)
    if media_dest.exists():
        shutil.rmtree(media_dest)
    shutil.copytree(STATIC_DIR, assets_dest)
    if MEDIA_DIR.exists():
        shutil.copytree(MEDIA_DIR, media_dest)

    admin_dir = assets_dest / 'admin'
    if admin_dir.exists():
        shutil.rmtree(admin_dir)

    for map_file in assets_dest.rglob('*.map'):
        map_file.unlink()


def main() -> None:
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    copy_assets()
    export_language('en', '')
    export_language('ar', 'ar')
    export_404()
    (DOCS_DIR / '.nojekyll').write_text('', encoding='utf-8')
    print('STATIC_EXPORT_DONE')


if __name__ == '__main__':
    main()
