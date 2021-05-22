from rest_framework_extensions.cache.decorators import CacheResponse
from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.constructors import KeyConstructor


class UserIdOrNoneKeyBit(bits.UserKeyBit):

    def get_data(self, params, view_instance, view_method, request, args, kwargs):
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            return self._get_id_from_user(request.user)
        else:
            return 'None'


class ExcludeQueryParamsKeyBit(bits.QueryParamsKeyBit):

    def __init__(self, params='*', exclude=None):
        self.exclude = [] if exclude is None else exclude
        super().__init__(params)

    def prepare_key_for_value_retrieving(self, key):
        return None if key in self.exclude else key


class NamedKeyConstructor(KeyConstructor):
    user = UserIdOrNoneKeyBit()
    query_params = ExcludeQueryParamsKeyBit(exclude=['cache', ])
    unique_view_id = bits.UniqueMethodIdKeyBit()
    format = bits.FormatKeyBit()

    def __init__(self, name, *args, **kwargs):
        self._name = name
        super().__init__(*args, **kwargs)

    def prepare_key(self, key_dict):
        user = key_dict.get('user')
        key = super().prepare_key(key_dict)
        return f'{self._name}_{user}_{key}'


class NamedKeyConstructorWithArgsKeyBit(NamedKeyConstructor):
    args = bits.ArgsKeyBit()


class ListSqlNamedKeyConstructor(NamedKeyConstructor):
    sql = bits.ListSqlQueryKeyBit()
    pagination = bits.PaginationKeyBit()


class RetrieveSqlNamedKeyConstructor(NamedKeyConstructor):
    sql = bits.RetrieveSqlQueryKeyBit()


class ControlledCacheResponse(CacheResponse):
    def process_cache_response(self, view_instance, view_method, request, args, kwargs):

        if request.GET.get('cache', None) is not None:
            key = self.calculate_key(
                view_instance=view_instance,
                view_method=view_method,
                request=request,
                args=args,
                kwargs=kwargs
            )
            self.cache.delete(key)

        return super().process_cache_response(view_instance, view_method, request, args, kwargs)


controlled_cache_response = ControlledCacheResponse
