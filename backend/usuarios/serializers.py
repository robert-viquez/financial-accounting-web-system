from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import ConfiguracionEmpresa, RegistroAuditoria


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


class UsuarioSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    correo = serializers.EmailField(source="email", required=False, allow_blank=True)
    roles = serializers.SlugRelatedField(
        source="groups",
        many=True,
        slug_field="name",
        queryset=Group.objects.all(),
        required=False,
    )

    class Meta:
        model = User
        fields = ["id", "username", "nombre", "first_name", "last_name", "correo", "roles", "is_active", "is_staff"]
        read_only_fields = ["username", "is_staff"]

    def get_nombre(self, obj) -> str:
        return obj.get_full_name() or obj.username


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


class RolSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    descripcion = serializers.CharField()

    def validate_nueva(self, value):
        validate_password(value, self.context["request"].user)
        return value
