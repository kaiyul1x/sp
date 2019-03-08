from rest_framework import serializers


class TaskSerializer(serializers.Serializer):
    increase_count = serializers.IntegerField(label='增加次数', max_value=2000, min_value=1)
    post_num = serializers.CharField(label='文章编号', max_length=255)
    csrf_token = serializers.CharField(label='CSRF_TOKEN', max_length=255)
    uuid = serializers.CharField(label='UUID', max_length=255)
