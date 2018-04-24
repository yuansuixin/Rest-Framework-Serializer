


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

- 从类的实例化开始，先找到`__new__()`,在Serializer类的父类BaseSerializer类中我们可以看到这个方法，

![Untitled-1-2018423201026](http://p693ase25.bkt.clouddn.com/Untitled-1-2018423201026.png)

![Untitled-1-2018423221514](http://p693ase25.bkt.clouddn.com/Untitled-1-2018423221514.png)

- many=True ,接下来执行ListSerializer对象的构造方法，many=False, 接下来执行UserInfoSerializer对象的构造方法 


- 知识点补充：
    - 类的实例化一般是将数据封装到对象中
    - 实例化的时候首先执行`__new__()`方法，这个方法返回的是一个对象，然后接下来去执行返回值的构造方法`__init__()`,注意一定是`__new__()`返回值的构造方法


###### 序列化
- 实例化完成之后，调用对象的data属性，从ser.data开始，data（）因为使用了property装饰器，所以调用的时候不需要些括号，data（）里调用了父类Serializer的data（），返回一个有序字典

- 这里分为了两路，一个是ListSerializer对象，一个是BaseSerializer对象，但是，这两个在本质上是一样的

> BaseSerializer对象

- 在Serializer的data（）调用了to_representation()方法，这里需要注意，我们现在已经是在BaseSerializer类中了，需要到Serializer类中找到这个方法，在这个方法里，循环遍历了定义的一些字段，调用了字段的get_attribute()方法， 如果字段时Field类型，就数据库中获取指定字段对应的值， 如果字段是HyperlinkedIdentityField类型的，则拿到当前行的对象obj，然后再执行每一个字段的to_representation（）方法，对拿到的值进行加工，最终转换成了反向生成的URl，返回回来

- 在fields类，get_attribute()方法，将序列化时传入的source参数的内容，使用点进行分隔开，赋值给source_attrs列表，循环遍历这个列表，`` instance = instance[attr]``,将instance变成了对象，然后再使用对象取值`` instance = getattr(instance, attr)``
- 使用is_simple_callable（）方法判断类型，是不是可执行的函数，如果可执行，直接执行

> ListSerializer对象的源码与上面相同

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

- 源码分析
    - 先进行实例化，然后从is_valid()开始，
    - 如果检验有错误就不会通过，返回一个布尔值
    - 调用了run_validation（），注意，这里已经到BaseSerializer类了，所以，我们要想看run_validation（）中的内容，需要返回到Serializer类中找
    - 在run_validation（）中，调用了run_validation（），同样的道理，需要到Serializer类中找，在run_validation（）方法中调用了to_internal_value（）， 
    - 在这个方法中，先通过getattr()拿到validate_字段名 属性值，默认是None，
    - 其实每个Field对象都有一个自己的正则验证，在验证之前，都需要执行字段本身的正则，也就是调用字段的run_validation（）
    - 如果找到了`validate_字段名`值，加了个括号，直接执行
    - 然后执行验证的钩子方法，在序列化验证的时候我们就可以定义一个`validate_字段名`方法，如果验证成功直接返回值，验证不通过抛出ValidationError

```
class UserGroupSerializer(serializers.Serializer):
    title = serializers.CharField(error_messages={'required':'标题不能为空'},validators=[XValidator('老女人'),])
    def validate_title(self,value):
        print(value)
        # 如果验证不通过
        # from rest_framework import exceptions
        # raise exceptions.ValidationError('看你不顺眼')
        # 验证通过
        return value

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