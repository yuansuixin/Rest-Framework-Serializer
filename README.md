


# 序列化

### 序列化数据

> 部分总结

- 写类

```
class UserInfoSerializer(serializers.ModelSerializer):
    '''
    ModelSerializer帮助我们找到数据库中对象的字段，并将其转换成对应的field对象，只是做的简单的转换
    '''
        class Meta:
        model = models.UserInfo
        # fields = '__all__'
        fields = ['id','username','password']
```
```
class RolesSerializer(serializers.Serializer):
    # 字段必须和数据库中的字段一致
    id = serializers.IntegerField()
    title = serializers.CharField()
```
- 字段
    - ``title = serializers.CharField(source='xx.xx.xx.xx')``
	- 自定义方法``title = serializers.SerializerMethodField()``
	- 自定义类

```
class UserInfoSerializer(serializers.ModelSerializer):
    rls = serializers.SerializerMethodField()  # 自定义显示,将数据序列化


    class Meta:
        model = models.UserInfo
        # fields = '__all__'
        fields = ['id','username','password','rls']


    def get_rls(self, row):
        '''
        函数名字必须是get开头，字段名称结尾
        :param row: 当前行的对象
        :return: 返回什么页面就会显示什么
        '''
        # 获取到所有的对象列表
        role_obj_list = row.roles.all()
        ret = []
        for item in role_obj_list:
            ret.append({'id': item.id, 'title': item.title})
        return ret
```

```
# 自定义类
class MyField(serializers.CharField):
    def to_representation(self, value):
        # value是从数据库中取到的值
        print(value)
        # 返回什么，页面就会显示什么
        return 'xxxx'

# 可以混合使用
class UserInfoSerializer(serializers.ModelSerializer):
    x1 = MyField(source='username')
```

- 自动序列化连表操作

```
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        # fields = '__all__'
        # fields = ['id','username','password','oooo','rls','group']
        depth = 1 # 表示往里面拿几层数据，默认是0，建议0-3之间

```
- 生成链接

```
class UserInfoSerializer(serializers.ModelSerializer):
    # 反向生成url,lookup_url_kwarg指的是url中的那个参数的值
    group = serializers.HyperlinkedIdentityField(view_name='gp',lookup_field='group_id',lookup_url_kwarg='pk')
    class Meta:
        model = models.UserInfo
        # fields = '__all__'
        fields = ['id','username','password','oooo','rls','group']
        # depth = 1 # 表示往里面拿几层数据，默认是0，建议0-3之间


class UserinfoView(APIView):
    def get(self,request):
        users = models.UserInfo.objects.all()
        ser = UserInfoSerializer(instance=users,many=True,context={'request':request})
        print(ser.data)
        ret = json.dumps(ser.data,ensure_ascii=False)
        return HttpResponse(ret)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserGroup
        fields = '__all__'


class GroupView(APIView):
    def get(self,request,*args,**kwargs):
        pk = kwargs.get('pk')
        obj = models.UserGroup.objects.filter(pk=pk).first()
        ser = GroupSerializer(instance=obj,many=False)
        ret = json.dumps(ser.data,ensure_ascii=False)
        return HttpResponse(ret)

```

```
urlpatterns = [
 url(r'^(?P<version>[v1|v2]+)/userinfo/$',views.UserinfoView.as_view(),name='userinfo'),
 url(r'^(?P<version>[v1|v2]+)/group/(?P<pk>\d+)$',views.GroupView.as_view(),name='gp'),

]
```

> 源码分析

###### 实例化
- 对象，Serializer类处理
- QuerySet，是使用ListSerializer类处理

- 从类的实例化开始，先找到__new__(),在Serializer类的父类BaseSerializer类中我们可以看到这个方法，

![Untitled-1-2018423201026](http://p693ase25.bkt.clouddn.com/Untitled-1-2018423201026.png)

![Untitled-1-2018423201525](http://p693ase25.bkt.clouddn.com/Untitled-1-2018423201525.png)

###### 序列化
- 从ser.data开始，data（）因为使用了property装饰器，所以调用的时候不需要些括号，data（）里调用了父类Serializer的data（），返回一个有序字典
- 在Serializer的data（）调用了to_representation()方法，在这个方法里，循环遍历了定义的一些字段，调用了字段的get_attribute()方法
- 在fields类，将传入的source参数的内容，使用点进行分隔开，赋值给source_attrs列表，循环遍历这个列表，`` instance = instance[attr]``,将instance变成了对象，然后再使用对象取值`` instance = getattr(instance, attr)``
- 使用is_simple_callable（）方法判断类型，是不是可执行的函数，如果可执行，直接执行

------------


- 知识点补充：
    - 类实例化的时候，先执行__new__(),才会执行__init__()方法
    - callback（），isinstance（）

```
def func(arg):
# 判断传入的参数是否是可执行的，也就是是不是函数类型
    #if callbale(arg):
	if isinstance(arg,types.FunctionType):
	    print(arg())
	else:
	    print(arg)

func(123)
func(lambda:'666')
```

### 请求数据校验

```
# 自定义验证规则
class XValidator(object):
    def __init__(self,base):
        self.base = base
    def __call__(self,value):
        if not value.startswith(self.base):
            message = '标题必须以%s开头'%self.base
            raise serializers.ValidationError(message)

    def set_context(self, serializer_field):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # 执行验证之前调用,serializer_fields是当前字段对象
        pass


class UserGroupSerializer(serializers.Serializer):
    title = serializers.CharField(error_messages={'required':'标题不能为空'},validators=[XValidator('老女人'),])


class UserGroupView(APIView):
    def post(self,request,*args,**kwargs):
        print(request.data)
        ser = UserGroupSerializer(data=request.data)
        # 数据校验，
        if ser.is_valid():
            print(ser.validated_data)
        else:
            print(ser.errors)
        return HttpResponse('提交数据')

```








