from rest_framework.metadata import SimpleMetadata

from waffle_protected_drf import is_drf_browsable_api_allowed


class WaffleProtectedSimpleMetadata(SimpleMetadata):
    """
    Disables metadata retrieval with OPTIONS request when the waffle flag is disabled.
    """

    always_expose_metadata_fields = ('renders', 'parses', 'actions')

    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)
        if not is_drf_browsable_api_allowed(request):
            metadata = {k: v for k, v in metadata.items()
                        if k in self.always_expose_metadata_fields}
            if 'actions' in metadata:
                metadata['actions'] = self.filter_actions(metadata['actions'])
        return metadata

    def filter_actions(self, actions):
        """Strip everything except choices"""
        stripped = {method: {field: dict(choices=field_info.get('choices'))
                             for field, field_info in method_info.items()
                             if field_info['type'] == 'choice'}
                    for method, method_info in actions.items()}
        # strip empty method_info dicts
        return {method: method_info for method, method_info in stripped.items() if method_info}
