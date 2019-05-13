import pytest
import time
from mixer.backend.django import mixer
from account.tokens import TokenGenerator
pytestmark = pytest.mark.django_db


class TestTokenGenerator:

    def test_make_hash_value(self):
        user = mixer.blend('account.User')
        timestamp = time.time()
        result = TokenGenerator._make_hash_value(self, user=user,
                                                 timestamp=timestamp)
        assert result == "{}{}{}".format(user.pk, timestamp, user.is_active)
