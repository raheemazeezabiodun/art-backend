# Third-Party Imports
from pycountry import countries
from rest_framework import serializers

# App Imports
from core import models


class OfficeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OfficeBlock
        fields = ("name", "id", "location")


class OfficeFloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OfficeFloor
        fields = ("number", "block", "id")


class OfficeFloorSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OfficeFloorSection
        fields = ("name", "floor", "id")


class OfficeFloorSectionDetailSerializer(serializers.ModelSerializer):
    """Serializer for selected office floor section detils"""

    block = serializers.SerializerMethodField()
    floor = serializers.SerializerMethodField()
    workspaces = serializers.SerializerMethodField()

    class Meta:
        model = models.OfficeFloorSection
        fields = ("id", "name", "floor", "block", "workspaces")

    def get_block(self, obj):
        """Returns block details for the section

        Args:
            obj (object): section object
        """
        return {"id": obj.floor.block.id, "name": obj.floor.block.name}

    def get_floor(self, obj):
        """Returns floor details for the section

        Args:
            obj ([object): section object
        """
        return {"id": obj.floor.id, "number": obj.floor.number}

    def get_workspaces(self, obj):
        """This method gets workspaces connected to the current
        office floor section current

        Args:
            obj (object): section object

        Returns:
            json: serialized workspaces
        """

        from api.serializers.andela_centres import OfficeWorkspaceSerializer

        workspaces = models.OfficeWorkspace.objects.filter(section=obj.id)
        serialized_workspaces = OfficeWorkspaceSerializer(workspaces, many=True)
        return serialized_workspaces.data


class OfficeWorkspaceSerializer(serializers.ModelSerializer):
    floor = serializers.ReadOnlyField(source="section.floor.number")
    block = serializers.ReadOnlyField(source="section.floor.block.name")
    section_name = serializers.ReadOnlyField(source="section.name")
    long_name = serializers.SerializerMethodField()

    class Meta:
        model = models.OfficeWorkspace
        fields = (
            "id",
            "name",
            "section",
            "section_name",
            "floor",
            "block",
            "long_name",
        )

    def get_long_name(self, obj):
        """This method creates a value for the long_name field

        Args:
            obj (object): current object being serialized.

        Returns:
            string: value for the long name field for each object.
        """
        block_name = obj.section.floor.block.name
        floor_number = obj.section.floor.number
        section_name = obj.section.name
        workspace_name = obj.name
        long_name = "{}-{}-{}-{}".format(
            block_name, floor_number, section_name, workspace_name
        )
        return long_name


class DepartmentSerializer(serializers.ModelSerializer):
    number_of_assets = serializers.SerializerMethodField()

    class Meta:
        model = models.Department
        fields = ("name", "id", "number_of_assets")

    def get_number_of_assets(self, obj):
        department_assignee = models.AssetAssignee.objects.filter(
            department_id=obj.id
        ).first()
        assets = models.Asset.objects.filter(assigned_to=department_assignee).count()
        return assets


class DepartmentDetailSerializer(serializers.ModelSerializer):
    assets_assigned = serializers.SerializerMethodField()

    class Meta:
        model = models.Department
        fields = ("name", "id", "assets_assigned")

    def get_assets_assigned(self, obj):
        """This method returns assets assigned to a particluar department

        Args:
            obj (object): current object instance being fetched

        Returns:
            json : serialized assets belonging to the specified department
        """

        from api.serializers.assets import DepartmentAssetSerializer

        department_assignee = models.AssetAssignee.objects.filter(
            department_id=obj.id
        ).first()
        assets = models.Asset.objects.filter(assigned_to=department_assignee)
        page = self.context["view"].paginate_queryset(assets)
        serialized_assets = DepartmentAssetSerializer(page, many=True)
        paginated_assets = self.context["view"].get_paginated_response(
            serialized_assets.data
        )
        return paginated_assets.data


class AndelaCentreSerializer(serializers.ModelSerializer):
    centre_name = serializers.ReadOnlyField(source="name")
    country = serializers.SlugRelatedField(
        queryset=models.Country.objects.all(), slug_field="name"
    )

    class Meta:
        model = models.AndelaCentre
        fields = ("id", "name", "country", "created_at", "last_modified", "centre_name")

    def to_internal_value(self, data):
        country_name = data.get("country")
        if not country_name:
            raise serializers.ValidationError(
                {"country": [self.error_messages["required"]]}
            )
        try:
            query_data = {"id": int(country_name)}
        except ValueError:
            country = countries.lookup(country_name)
            query_data = {"name": country.name}
        finally:
            try:
                country = models.Country.objects.get(**query_data)
            except Exception:
                raise serializers.ValidationError(
                    {
                        "country": [
                            f'Invalid country "{country_name}" - object does not exist.'
                        ]
                    }
                )
        data_ = data.copy()
        data_["country"] = country.name
        if not data_.get("name"):
            data_["name"] = data_.get("centre_name")
        internal_value = super().to_internal_value(data_)
        return internal_value


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ("id", "name", "created_at", "last_modified")
