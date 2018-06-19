import sys
import os
import csv
from tqdm import tqdm
import django

from .helpers import display_inserted, display_skipped

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from core.models.asset import (
    AssetType, AssetMake, Asset, AssetModelNumber, AssetCategory,
    AssetSubCategory,
)   # noqa


def post_asset_make(f, file_length):
    """
    Bulk creates asset make
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            make_label = row.get('asset_make', '').strip()
            asset_type = row.get('asset_type', '').strip()
            if not make_label:
                skipped[row['']] = [
                    ('asset_make has no value'.
                     format(row['asset_make'])), counter]

            elif not asset_type:
                skipped[row['asset_type']] = [
                    ('asset type {0} does not exist'.
                     format(row['asset_type'])), counter]

            else:
                asset_make = AssetMake.objects.\
                    filter(make_label=row['asset_make'])\
                    .exists()
                asset_type = AssetType.objects.filter(asset_type=row[
                    'asset_type']).exists()

                if asset_make:
                    skipped[row['asset_make']] = [
                        ('asset_make {0} already exists'.
                            format(row['asset_make'])), counter]
                elif not asset_type:
                    skipped[row['asset_type']] = [
                        ('asset type {0} does not exist'.
                            format(row['asset_type'])), counter]

                else:
                    asset_type = AssetType.objects.filter(
                        asset_type=row['asset_type']
                    ).first()
                    new_asset_make = AssetMake.objects.\
                        create(make_label=row['asset_make'],
                               asset_type=asset_type)

                    new_asset_make.save()
                    inserted_records.append([new_asset_make, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET MAKES")
    display_skipped(skipped)


def post_asset(f, file_length):
    """
    Bulk creates assets
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            model_number = row.get('model_number', '').strip()
            asset_code = row.get('asset_code', '').strip()
            serial_number = row.get('serial_number', '').strip()

            if model_number and asset_code and serial_number:
                model_number_status = AssetModelNumber.objects.\
                    filter(model_number=model_number)\
                    .exists()
                asset_code_status = Asset.objects.filter(
                    asset_code=asset_code).exists()
                serial_number_status = Asset.objects.filter(
                    serial_number=serial_number).exists()
                if asset_code_status:
                    skipped[asset_code] = [
                        ('asset_code {0} already exists'.
                         format(asset_code)), counter]
                elif serial_number_status:
                    skipped[serial_number] = [
                        ('serial_number {0} already exists'.
                         format(serial_number)), counter]
                elif not model_number_status:
                    skipped[model_number] = [('model number {0} does '
                                              'not exist'.
                                              format(model_number)), counter]
                else:
                    asset = Asset()
                    asset.asset_code = asset_code
                    asset.serial_number = serial_number
                    asset.model_number = AssetModelNumber.objects.\
                        get(model_number=model_number)
                    asset.save()
                    inserted_records.append([asset, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSETS")
    display_skipped(skipped)


def post_asset_category(f, file_length):
    """
    Bulk creates asset category
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            assets_category = row.get('Category', '').strip()

            if not assets_category:
                skipped[assets_category] = [
                    'Category has no value', counter]

            else:
                assets_category_status = AssetCategory.objects. \
                    filter(category_name=assets_category).exists()
                if assets_category_status:
                    skipped[row['Category']] = [('Category {0} already '
                                                 'exists'.
                                                 format(assets_category)),
                                                counter]
                else:
                    new_asset_category = AssetCategory.objects.create(
                        category_name=assets_category
                    )
                    new_asset_category.save()
                    inserted_records.append([
                        new_asset_category,
                        counter]
                    )

            counter += 1
            pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET CATEGORIES")
    display_skipped(skipped)


def post_asset_subcategory(f, file_length):
    """
    Bulk creates asset category
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            assets_category = row.get('Category', '').strip()
            assets_subcategory = row.get('Sub-Category', '').strip()
            if not assets_category:
                skipped[assets_category] = [
                    'Category has no value', counter]
            elif not assets_subcategory:
                skipped[assets_subcategory] = [
                    'Sub-Category has no value', counter]

            else:
                assets_category_status = AssetCategory.objects. \
                    filter(category_name=assets_category).exists()
                assets_subcategory_status = AssetSubCategory.objects. \
                    filter(sub_category_name=assets_subcategory).exists()
                if assets_category_status and assets_subcategory_status:
                    skipped[assets_subcategory] = [
                        ('Sub Category {0} already exists'.
                            format(assets_subcategory)), counter]

                elif assets_category_status and not assets_subcategory_status:
                    category = AssetCategory.objects.\
                        filter(category_name=assets_category).first()
                    new_asset_subcategory = AssetSubCategory.objects.create(
                        sub_category_name=assets_subcategory,
                        asset_category=category
                    )
                    new_asset_subcategory.save()
                    inserted_records.append([
                        new_asset_subcategory,
                        counter]
                    )
                else:
                    new_asset_category = AssetCategory.objects.create(
                        category_name=assets_category
                    )
                    new_asset_category.save()
                    category = AssetCategory.objects.filter(
                        category_name=assets_category).first()
                    new_asset_subcategory = AssetSubCategory.objects.create(
                        sub_category_name=assets_subcategory,
                        assets_category=category
                    )
                    new_asset_subcategory.save()

                    inserted_records.append([
                        new_asset_subcategory,
                        counter]
                    )

            counter += 1
            pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET SUB-CATEGORIES")
    display_skipped(skipped)


def post_asset_model_no(f, file_length):
    """
    Bulk creates asset model number
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            asset_make = row.get('asset_make', '')
            model_number = row.get('model_number', '')

            if asset_make and model_number:
                asset_model_no = AssetModelNumber.objects.\
                    filter(model_number=model_number)\
                    .exists()
                asset_make_status = AssetMake.objects.filter(
                    make_label=asset_make).exists()

                if asset_model_no:
                    skipped[row['asset_make']] = [
                        ('asset_model_no {0} already exists'.
                         format(model_number)), counter]
                elif not asset_make_status:
                    skipped[asset_make] = [
                        ('asset make {0} does not exist'.
                         format(asset_make)), counter]

                else:
                    new_asset_model_no = AssetModelNumber()
                    new_asset_model_no.model_number = model_number
                    new_asset_model_no.make_label = AssetMake.objects.get(
                        make_label=asset_make
                    )
                    new_asset_model_no.save()
                    inserted_records.append([new_asset_model_no, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET MODELS")
    display_skipped(skipped)


def post_asset_types(f, file_length):
    """
    Bulk creates asset types
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            asset_type = row.get('asset_type', '').strip()
            sub_category = row.get('Sub-Category', '').strip()
            if asset_type and sub_category:
                sub_category_name = AssetSubCategory.objects.\
                    filter(sub_category_name=sub_category)\
                    .exists()
                asset_type_status = AssetType.objects.filter(
                    asset_type=asset_type
                ).exists()
                if not sub_category_name:
                    skipped[sub_category] = [
                        ('Sub Category {0} does not exist'.
                         format(sub_category)), counter]
                elif asset_type_status:
                    skipped[asset_type] = [
                        ('asset_type {0} already exists'.
                         format(asset_type)), counter]
                else:
                    asset = AssetType()
                    asset.asset_type = asset_type
                    asset.asset_sub_category = AssetSubCategory.objects.\
                        get(sub_category_name=sub_category)
                    asset.save()
                    inserted_records.append([asset, counter])
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET TYPES")
    display_skipped(skipped)
