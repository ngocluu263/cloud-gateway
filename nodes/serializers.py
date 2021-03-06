from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer
from nodes.models import Nodes
from users.models import User


class NodeSerializer(DocumentSerializer):
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects)
    label = serializers.CharField(min_length=4, max_length=28)
    # extra field
    url = serializers.HyperlinkedIdentityField(
        view_name='nodes-detail',
        lookup_field='pk'
    )
    sensor_count = serializers.SerializerMethodField()
    sensors_list = serializers.HyperlinkedIdentityField(
        view_name='node-sensors-list',
        lookup_field='pk'
    )
    subscriptions_list = serializers.HyperlinkedIdentityField(
        view_name='subscription-filter-node',
        lookup_field='label',
        lookup_url_kwarg='node'
    )

    def validate_label(self, value):
        """
        rest_framework.validators.UniqueValidator can't handle label uniqueness
        if we just want to avoid the same label for a user but let it for other user
        :param value: self.label
        :return: validated value
        """
        user = self.context.get('request').user
        node = Nodes.objects.filter(user=user, label=value)

        # when updating instance
        if None is not self.instance:
            if not node or self.instance.label == value:
                return value
        elif not node: # when create new instance
            return value
        raise serializers.ValidationError("This field must be unique.")

    @staticmethod
    def get_sensor_count(obj):
        return obj.sensors.count()

    class Meta:
        model = Nodes
        exclude = ('sensors',)

    def create(self, validated_data):
        node = Nodes.objects.create(**validated_data)
        node.subsperdayremain = node.subsperday
        node.save()
        return node

    def update(self, instance, validated_data):
        instance.label = validated_data.get('label', instance.label)
        instance.secretkey = validated_data.get('secretkey', instance.secretkey)
        instance.subsperday = validated_data.get('subsperday', instance.subsperday)
        instance.subsperdayremain = validated_data.get('subsperday', instance.subsperday)
        instance.save()
        return instance