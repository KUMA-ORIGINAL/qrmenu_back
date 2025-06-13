from datetime import timedelta
from pathlib import Path

import environ
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

import account

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)

SECRET_KEY = env('SECRET_KEY')

DEBUG = bool(env("DEBUG", default=0))

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS").split(" ")

DOMAIN = env("DOMAIN")

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ["Authorization", "Content-Type", "Accept"]

if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


INSTALLED_APPS = [
    'daphne',
    'modeltranslation',
    'unfold',
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.postgres",

    'rest_framework',
    'drf_spectacular',
    'django_filters',
    'corsheaders',
    'cachalot',
    'channels',
    "phonenumber_field",
    'axes',

    'menu',
    'account',
    'venues',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'djangorestframework_camel_case.middleware.CamelCaseMiddleWare',
    'config.middleware.LanguageMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'orders/templates',
            BASE_DIR / 'account/templates',
            BASE_DIR / 'menu/templates',
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'site_icons/',
    BASE_DIR / 'account/static/'
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_PARAMETERS = ["username", ["username", "user_agent"]]
AXES_RESET_ON_SUCCESS = True
AXES_ONLY_ADMIN_SITE = True
AXES_USERNAME_FORM_FIELD = "username"


TG_BOT_TOKEN = env('TG_BOT_TOKEN')

SMS_LOGIN=env("SMS_LOGIN")
SMS_PASSWORD=env("SMS_PASSWORD")
SMS_SENDER=env("SMS_SENDER")

RECEIPT_MQTT_BROKER = "193.176.239.186"
RECEIPT_MQTT_PORT = 1883
RECEIPT_MQTT_USERNAME = "myuser"
RECEIPT_MQTT_PASSWORD = "123456"

POSTER_APPLICATION_ID = env('POSTER_APPLICATION_ID')
POSTER_APPLICATION_SECRET = env('POSTER_APPLICATION_SECRET')
POSTER_REDIRECT_URI = env('POSTER_REDIRECT_URI')

PHONENUMBER_DEFAULT_REGION = 'KG'

LANGUAGES = (
    ('ru', 'Russian'),
    ('en', 'English'),
    ('ky', 'Kyrgyz'),
)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_LANGUAGES = ('ru', 'en', 'ky')
MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('ru',),
    'en': ('ru', 'ky'),  # Для английского fallback на русский и кыргызский
    'ky': ('ru',),  # Для кыргызского fallback на русский
}
MODELTRANSLATION_AUTO_POPULATE = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_TRUSTED_ORIGINS = [f"https://{DOMAIN}", f"http://{DOMAIN}"]

AUTH_USER_MODEL = 'account.User'

if DEBUG:
    INSTALLED_APPS += ['silk']
    MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CACHALOT_ENABLED = True

CACHALOT_ONLY_CACHABLE_TABLES = (
    'menu.category',
    'menu.product',
    'menu.modificator',

    'venues.banner',
    'venues_venue',
    'venues_spot',
    'venues_hall',
    'venues_table',

    'orders_paymentaccount',
)

CACHALOT_TIMEOUT = 60 * 30  # 30 минут

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": ['redis://redis:6379/2'],  # Используем другой слот Redis (например, /2)
        },
    },
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'QR menu',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SCHEMA_VERSION': '3.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CAMELIZE_NAMES': True,

    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields',
    ],

    'SERVE_PUBLIC': True,
    'SERVE_HTTPS': True,
    'SERVE_PERMISSIONS': ['config.permissions.IsSuperUser'],
    'SERVE_AUTHENTICATION': ['rest_framework.authentication.SessionAuthentication',]
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "AUTH_HEADER_TYPES": ("Bearer",),
    'UPDATE_LAST_LOGIN': True,
}

DJOSER = {
    # 'SERIALIZERS': {
    #     'user': 'account.serializers.UserSerializer',
    #     'current_user': 'account.serializers.UserSerializer',
    # },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} - {asctime} - {module} - {name} - {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} - {module} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',  # Можно изменить на 'DEBUG' для более подробного вывода
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',  # Логи с уровнем DEBUG и выше будут записываться в файл
            'class': 'logging.FileHandler',
            'filename': 'django_app.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        # },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'services.poster': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        }
    },
}

UNFOLD = {
    "SITE_TITLE": 'iMenu.kg',
    "SITE_HEADER": "iMenu.kg",
    "SITE_URL": "/",
    "SITE_SYMBOL": "menu",  # symbol from icon set
    "SHOW_HISTORY": True, # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True, # show/hide "View on site" button, default: True
    "DASHBOARD_CALLBACK": "orders.dashboard.dashboard_callback",
    "LOGIN": {
        "image": lambda request: static("login-bg.jpg"),
    },
    "BORDER_RADIUS": "6px",
    "COLORS": {
        "base": {
            "50": "249 250 251",
            "100": "243 244 246",
            "200": "229 231 235",
            "300": "209 213 219",
            "400": "156 163 175",
            "500": "107 114 128",
            "600": "75 85 99",
            "700": "55 65 81",
            "800": "31 41 55",
            "900": "17 24 39",
            "950": "3 7 18",
        },
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",  # text-base-500
            "subtle-dark": "var(--color-base-400)",  # text-base-400
            "default-light": "var(--color-base-600)",  # text-base-600
            "default-dark": "var(--color-base-300)",  # text-base-300
            "important-light": "var(--color-base-900)",  # text-base-900
            "important-dark": "var(--color-base-100)",  # text-base-100
        },
    },
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Навигация"),
                "items": [
                    {
                        "title": _("Панель"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Заведения"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Заведение"),
                        "icon": "store",
                        "link": reverse_lazy("admin:venues_venue_changelist"),
                        "permission": "account.utils.permission_callback_for_admin",
                    },
                    {
                        "title": _("Точки заведения"),
                        "icon": "explore_nearby",
                        "link": reverse_lazy("admin:venues_spot_changelist"),
                    },
                    {
                        "title": _("Залы"),
                        "icon": "hub",
                        "link": reverse_lazy("admin:venues_hall_changelist"),
                    },
                    {
                        "title": _("Столы"),
                        "icon": "table_restaurant",
                        "link": reverse_lazy("admin:venues_table_changelist"),
                    },
                    {
                        "title": _("Рекламные баннеры"),
                        "icon": "photo_library",
                        "link": reverse_lazy("admin:venues_banner_changelist"),
                    },
                ],
            },
            {
                "title": _("Меню"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Категории"),
                        "icon": "category",
                        "link": reverse_lazy("admin:menu_category_changelist"),
                    },
                    {
                        "title": _("Товары"),
                        "icon": "menu_book",
                        "link": reverse_lazy("admin:menu_product_changelist"),
                    },
                ],
            },
            {
                "title": _("Транзакции и Платежи"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Транзакции"),
                        "icon": "account_balance_wallet",
                        "link": reverse_lazy("admin:orders_transaction_changelist"),
                    },
                    {
                        "title": _("Платёжные аккаунты"),
                        "icon": "credit_card",
                        "link": reverse_lazy("admin:orders_paymentaccount_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                "title": _("Заказы и Клиенты"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Заказы"),
                        "icon": "shopping_bag",
                        "link": reverse_lazy("admin:orders_order_changelist"),
                    },
                    {
                        "title": _("Клиенты"),
                        "icon": "groups",
                        "link": reverse_lazy("admin:orders_client_changelist"),
                    },
                ],
            },
            {
                "title": _("Чеки"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Чеки"),
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:orders_receipt_changelist"),
                    },
                    {
                        "title": _("Принтеры для чека"),
                        "icon": "print",
                        "link": reverse_lazy("admin:orders_receiptprinter_changelist"),
                    },
                ],
            },
            {
                "title": _("Пользователи и Доступ"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Пользователи"),
                        "icon": "person",
                        "link": reverse_lazy("admin:account_user_changelist"),
                        "permission": "account.utils.permission_callback_for_admin",
                    },
                    {
                        "title": _("Группы"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                "title": _("Системные настройки"),
                "items": [
                    {
                        "title": _("POS системы"),
                        "icon": "contactless",
                        "link": reverse_lazy("admin:venues_possystem_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                "title": _("Безопасность"),
                "items": [
                    {
                        "title": _("Попытки входа (Axes)"),
                        "icon": "shield",
                        "link": reverse_lazy("admin:axes_accessattempt_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Логи входа (Axes)"),
                        "icon": "history",
                        "link": reverse_lazy("admin:axes_accesslog_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Логи блокировок (Axes)"),
                        "icon": "lock",
                        "link": reverse_lazy("admin:axes_accessfailurelog_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },

        ],
    }
}
