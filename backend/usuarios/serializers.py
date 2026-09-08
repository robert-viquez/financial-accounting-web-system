from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import ConfiguracionEmpresa, RegistroAuditoria


def permisos_negocio():
    return Permission.objects.exclude(
        content_type__app_label__in=["admin", "auth", "contenttypes", "sessions"]
    )


class ConfiguracionEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionEmpresa
        fields = "__all__"
        read_only_fields = ["actualizado_en"]

    def validate_logo(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("El logo no puede superar 5 MB.")
        return value


class IdentidadEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionEmpresa
        fields = ["nombre", "logo"]


class PerfilSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    correo = serializers.EmailField(source="email", required=False, allow_blank=True)
    roles = serializers.SlugRelatedField(source="groups", many=True, slug_field="name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "nombre", "first_name", "last_name", "correo", "roles", "is_active", "is_staff", "is_superuser"]
        read_only_fields = ["username", "roles", "is_active", "is_staff", "is_superuser"]

    def get_nombre(self, obj) -> str:
        return obj.get_full_name() or obj.username


class UsuarioAdminSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    correo = serializers.EmailField(source="email", required=False, allow_blank=True)
    roles = serializers.SlugRelatedField(
        source="groups", many=True, slug_field="name", queryset=Group.objects.all(), required=False
    )
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id", "username", "nombre", "first_name", "last_name", "correo", "roles",
            "is_active", "is_staff", "is_superuser", "password",
        ]
        read_only_fields = ["is_superuser"]

    def get_nombre(self, obj) -> str:
        return obj.get_full_name() or obj.username

    def validate(self, attrs):
        request = self.context["request"]
        instance = self.instance
        if instance and instance.is_superuser and not request.user.is_superuser:
            raise serializers.ValidationError("Solo un superusuario puede modificar otro superusuario.")
        if "is_staff" in attrs and not request.user.is_superuser:
            current = instance.is_staff if instance else False
            if attrs["is_staff"] != current:
                raise serializers.ValidationError({"is_staff": "Solo un superusuario puede cambiar este estado."})
        if instance == request.user and attrs.get("is_active") is False:
            raise serializers.ValidationError({"is_active": "No puede desactivar su propia cuenta."})
        if instance and instance.is_superuser and attrs.get("is_staff") is False:
            raise serializers.ValidationError({"is_staff": "Un superusuario debe conservar el estado staff."})
        return attrs

    def validate_password(self, value):
        validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        groups = validated_data.pop("groups", [])
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "La contraseña es obligatoria."})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop("groups", None)
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        if groups is not None:
            instance.groups.set(groups)
        return instance


class PasswordAdministrativoSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        validate_password(value, self.context["target_user"])
        return value


class PermisoSerializer(serializers.ModelSerializer):
    aplicacion = serializers.CharField(source="content_type.app_label", read_only=True)
    modelo = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "aplicacion", "modelo"]


class RolAdminSerializer(serializers.ModelSerializer):
    permisos = serializers.PrimaryKeyRelatedField(
        source="permissions", many=True, queryset=permisos_negocio(), required=False
    )
    usuarios = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "permisos", "usuarios"]

    def get_usuarios(self, obj):
        return [{"id": user.id, "username": user.username} for user in obj.user_set.order_by("username")]


class CambiarPasswordSerializer(serializers.Serializer):
    actual = serializers.CharField(write_only=True)
    nueva = serializers.CharField(write_only=True)

    def validate_actual(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("La contraseña actual no es correcta.")
        return value


class RegistroAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = RegistroAuditoria
        fields = "__all__"
