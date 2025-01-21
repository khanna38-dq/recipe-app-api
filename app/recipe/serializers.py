"""
Serializers for recipe app
"""

from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ("id", "name")
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object"""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ("id", "title", "time_minutes", "price", "link", "tags", "ingredients")
        read_only_fields = ("id",)

    def _get_or_create_tag(self, tags, recipe):
        """Handle getting or creating a tag"""
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredient(self, ingredients, recipe):
        """Handle getting or creating an ingredient"""
        auth_user = self.context["request"].user
        for ingredient in ingredients:
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                user=auth_user, **ingredient
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a new recipe"""
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_ingredient(ingredients, recipe)
        self._get_or_create_tag(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update a recipe"""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tag(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredient(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the recipe detail object"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ("description",)
