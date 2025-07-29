from rest_framework import serializers
from ft.user.models import Membership


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
        }

    def validate(self, data):
        is_active = data.get(
            "is_active", self.instance.is_active if self.instance else True
        )
        if not is_active:
            return data

        user = self.context["request"].user if not self.instance else self.instance.user
        start_date = data.get(
            "start_date", self.instance.start_date if self.instance else None
        )
        end_date = data.get(
            "end_date", self.instance.end_date if self.instance else None
        )

        overlapping = Membership.objects.filter(
            user=user,
            is_active=True,
        ).exclude(pk=self.instance.pk if self.instance else None)

        overlapping = overlapping.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if overlapping.exists():
            raise serializers.ValidationError(
                "Cet utilisateur a déjà une adhésion active pendant cette période."
            )

        return data
