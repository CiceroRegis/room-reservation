import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE, ALL_ATTRIBUTES

UserModel = get_user_model()
logger = logging.getLogger('django')


class LDAPBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            ldap_conn = self.connect(username, password)
        except Exception as e:
            logger.error('Authentication ldap error', exc_info=e)
            return None

        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            return self.check_and_create_user(ldap_conn, username)
        else:
            if self.user_can_authenticate(user):
                return user

    @staticmethod
    def connect(username, password):
        ldap_dc, ldap_sub = settings.LDAP_RESOURCE.split('.')
        return Connection(
            Server(settings.LDAP_HOST, port=636, use_ssl=True),
            auto_bind=AUTO_BIND_NO_TLS,
            read_only=True,
            check_names=True,
            user="%s\\%s" % (ldap_dc, username,), password=password
        )

    @staticmethod
    def check_and_create_user(ldap_conn, username):
        ldap_conn.search(
            search_base='DC=%s' % str.join(',DC=', settings.LDAP_RESOURCE.split('.')),
            search_filter="(&(sAMAccountName=%s))" % username,
            search_scope=SUBTREE,
            attributes=ALL_ATTRIBUTES,
            get_operational_attributes=True)

        result = json.loads(ldap_conn.response_to_json()).get('entries', [])
        if len(result) < 1 or len(result) > 1:
            logger.warning('Data user ldap return: {0}'.format(str(result)))
            return None

        user_ad_attrs = result[0].get('attributes', None)
        user_email = user_ad_attrs.get('mail') if user_ad_attrs.get('mail') else user_ad_attrs.get('userPrincipalName')
        try:
            user_first_name = user_ad_attrs.get('displayName').split(' ')
            user = UserModel(
                first_name=user_first_name[0],
                last_name=' '.join(user_first_name[1:]),
                username=username,
                email=user_email,
                is_staff=True,
                is_superuser=False,
                is_active=True
            )
            user.save()
            return user
        except Exception as e:
            logger.error('Error save user ldap in application database', exc_info=e)
            return None
