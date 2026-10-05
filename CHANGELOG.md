# Changelog

Історія розробки проєкту за кроками дорожньої карти з ТЗ (розділ 11).
Кожен крок відповідає окремому архіву-комітом.

## Крок 1 — Ініціалізація проєкту

- Налаштовано менеджер залежностей **uv** (`pyproject.toml`).
- Multi-stage `Dockerfile` (builder на `uv` + мінімальний runner-образ).
- `docker-compose.yml`: сервіси `web` + `db` (PostgreSQL 16), у
  розширеному стилі - іменована мережа `hopbarley_network`,
  healthcheck для обох сервісів, іменовані volumes, усі порти
  налаштовуються через `.env` (`DB_EXTERNAL_PORT`, `WEB_EXTERNAL_PORT`).
  Цей файл створюється один раз на Кроці 1 і далі не змінюється.
- `entrypoint.sh`: очікування БД, `makemigrations`/`migrate`, `collectstatic`.
- Базовий скелет Django-проєкту (`config/`: settings/urls/wsgi/asgi).
- Підключено шаблони (`templates/base.html`) та статику (`static/`,
  скопійована з оригінального HTML-дизайну Hop & Barley) - перевірено
  тимчасовою заглушкою на `/`.
- **CI/CD**: базовий `.github/workflows/ci.yml` (GitHub Actions) -
  навмисно заведений одразу на першому кроці, а не "під кінець для
  галочки". Перевіряє встановлення залежностей (`uv sync`),
  застосування міграцій та `manage.py check` на кожен push/PR.
  Розширюватиметься на Кроках 9-10 (валідація API-схеми, лінтери,
  тести).

## Крок 2 — Створення моделей

- Додано застосунки `apps.products`, `apps.orders`, `apps.reviews`.
- Моделі: `Category` (з вкладеністю через `parent`), `Product`,
  `Order`/`OrderItem` (зі снепшотом ціни на момент покупки), `Review`
  (унікальний на пару користувач+товар, рейтинг 1-5).
- Базова реєстрація моделей в адмін-панелі (без кастомізації - вона
  з'явиться на Кроці 8).
- Додано `Pillow` до залежностей (потрібен для `Product.image`).
- Міграції генеруються автоматично при старті контейнера
  (`entrypoint.sh` викликає `makemigrations` перед `migrate`).

## Крок 3 — Реалізація каталогу

- `django-filter` + `ProductFilter` (фільтр за категорією-slug та
  діапазоном цін).
- `ProductListView` (CBV): пошук за назвою/описом, сортування
  (новизна/ціна/рейтинг), пагінація (`paginate_by=9`).
- `Product.objects` - кастомний `ProductQuerySet` (`active()`,
  `with_rating()` - анотація середнього рейтингу через `Avg`/`Count`,
  оптимізовано через `select_related("category")` - уникнення N+1).
- Шаблон `templates/products/catalog.html` (картки поки не клікабельні -
  сторінка товару з'явиться на Кроці 4).
- `/` та `/products/` тепер ведуть на каталог (заглушку прибрано).
- Команда `python manage.py seed_data` - наповнення демо-товарами.

## Крок 4 — Сторінка товару та відгуки

- `ProductDetailView` (`/product/<slug>/`): опис, ціна, зображення,
  середній рейтинг, список відгуків.
- `ReviewForm` + `FormMixin`: форма відгуку доступна лише авторизованим
  користувачам, які реально купили товар (перевірка через
  `OrderItem.objects.filter(order__user=..., product=...)`), і лише
  один відгук на товар (`UniqueConstraint` на рівні моделі + перевірка
  у view).
  Автентифікація повноцінного веб-кабінету ще не готова (буде на
  Кроці 7) - тимчасово для входу можна користуватись адмінкою.
- Картки каталогу тепер клікабельні й ведуть на сторінку товару.
- Кнопка "Додати в кошик" показана як прев'ю UI (неактивна) - кошик
  запрацює на Кроці 5.

## Крок 5 — Кошик

- `apps/orders/cart.py`: клас `Cart` на основі сесій Django (без
  окремої моделі БД), з обмеженням кількості за наявним залишком на
  складі (`product.stock`).
- `context_processors.cart` - кошик доступний у будь-якому шаблоні
  (`{{ cart }}`), лічильник товарів у шапці сайту.
- `/cart/`, `/cart/add/<id>/`, `/cart/remove/<id>/`.
- Кнопку "Додати в кошик" на сторінці товару активовано.
- Кнопка "Оформити замовлення" поки неактивна - checkout на Кроці 6.

## Крок 6 — Оформлення замовлення та email

- `CheckoutForm` (ПІБ, email, телефон, адреса доставки, спосіб оплати).
- `CheckoutView`: атомарне створення `Order`+`OrderItem`
  (`transaction.atomic`), списання залишків на складі, перевірка на
  перевищення залишків перед оформленням.
- `apps/orders/emails.py`: email-підтвердження клієнту та сповіщення
  адміністратору (`EMAIL_BACKEND=console` у DEBUG - листи видно в
  логах контейнера `web`).
- `/cart/checkout/`, `/cart/checkout/success/` (доступні лише
  авторизованим - `LoginRequiredMixin`, тимчасово через `/admin/login/`,
  повноцінний логін покупців - Крок 7).

## Крок 7 — Особистий кабінет

- `apps.users`: модель `Profile` (OneToOne до `User`, автостворення
  через сигнал `post_save`), `RegisterForm`/`UserUpdateForm`/
  `ProfileUpdateForm`.
- `/account/register/`, `/account/login/`, `/account/logout/`,
  `/account/` (історія замовлень з фільтром за статусом),
  `/account/edit/` (редагування профілю), `/account/password/`.
- `LOGIN_URL` тепер вказує на `users:login` (замість тимчасового
  `/admin/login/` з Кроку 6).
- Header (`base.html`) отримав повноцінну навігацію: Sign in/Register
  для анонімів, посилання на кабінет+Sign out для авторизованих.

## Крок 8 — Кастомізація адмін-панелі та аналітика

- `ProductAdmin`: мініатюра зображення, `list_editable` (ціна/залишок/
  активність прямо в списку), кастомний фільтр `StockLevelFilter`
  (немає в наявності / мало / достатньо), масові дії (активувати/
  деактивувати товари).
- `OrderAdmin`: інлайн-редагування позицій замовлення, масові дії
  (позначити оплаченими/відправленими), `date_hierarchy`.
- Окрема сторінка **"Аналітика продажів"** (`/admin/orders/order/analytics/`):
  загальний виторг, кількість замовлень, середній чек, топ-10 товарів
  за кількістю продажів - кнопка над списком замовлень в адмінці.

## Крок 9 — REST API, JWT, документація

- Додано `djangorestframework`, `djangorestframework-simplejwt`,
  `drf-spectacular`, `django-cors-headers`.
- `ProductViewSet` (read-only), `OrderViewSet` (CRUD лише власних
  замовлень користувача), `CartAPIView`/`CartItemAPIView`,
  `ReviewViewSet` (вкладений під товар), `RegisterAPIView`/
  `LoginAPIView` (JWT access+refresh)/`MeAPIView`.
- Swagger UI (`/api/docs/`), ReDoc (`/api/redoc/`), OpenAPI-схема
  (`/api/schema/`) - через `drf-spectacular`.
- JWT: access-токен 15 хв, refresh - 7 днів, ротація + blacklist
  після ротації.
- `IsAuthenticatedOrReadOnly` за замовчуванням; users бачать і можуть
  редагувати лише свої замовлення/відгуки (перевірка на рівні
  `get_queryset()`/`perform_create()`).

## Крок 10 — Якість: тести, типізація, лінтери

- CI (`.github/workflows/ci.yml`) істотно розширено: тепер це основний
  момент, коли пайплайн, запущений ще на Кроці 1, стає "повним" -
  додано `flake8`, `mypy` та `uv run pytest --cov`, встановлення
  залежностей перейшло на `uv sync --extra dev`.

- `pytest-django`: тести кошика, checkout (транзакції + списання
  складу), відгуків ("лише після покупки"), веб-каталогу, REST API
  (товари, JWT реєстрація/логін, ізоляція замовлень між користувачами).
- `flake8` (`setup.cfg`) та `mypy` + `django-stubs`/
  `djangorestframework-stubs` (`mypy.ini`).
- Dev-залежності винесено в `[project.optional-dependencies].dev`
  (`uv sync --extra dev` локально); у Docker-образі встановлені завжди
  для зручності `docker-compose exec web pytest`.
