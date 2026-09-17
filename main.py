import os
import json
import asyncio

import disnake
from disnake.ext import commands, tasks


# ==========================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ==========================================

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ==========================================
# ID И НАСТРОЙКИ
# ==========================================

CATEGORY_TICKETS_ID = 1543635533375475833
STAFF_LOG_CHANNEL_ID = 1543652454229352448
STAFF_ROLE_ID = 1543621903539769344

COUNTER_CHANNEL_ID = 1550279189582848102


# ==========================================
# БАННЕРЫ
# ==========================================

BANNER_STORE_MAIN = (
    "https://cdn.discordapp.com/attachments/"
    "1543629832167104528/1543648642152398948/"
    "Picsart_26-08-30_18-18-35-370.png"
)

BANNER_STORE_DS = (
    "https://cdn.discordapp.com/attachments/"
    "1543629832167104528/1543648640847970384/"
    "Picsart_26-08-30_18-19-53-903.png"
)

BANNER_STORE_BOOST = (
    "https://cdn.discordapp.com/attachments/"
    "1543629832167104528/1543648640449642598/"
    "Picsart_26-08-30_18-20-30-349.png"
)

BANNER_STORE_STEAM = (
    "https://cdn.discordapp.com/attachments/"
    "1543629832167104528/1543648640118030376/"
    "Picsart_26-08-30_18-20-41-435.png"
)

BANNER_STAFF = (
    "https://cdn.discordapp.com/attachments/"
    "1543629832167104528/1543648641636507699/"
    "Picsart_26-08-30_18-19-27-501.png"
)

BANNER_SUPPORT = (
    "https://cdn.discordapp.com/attachments/"
    "1543629832167104528/1543648641242239056/"
    "Picsart_26-08-30_18-19-41-401.png"
)


# ==========================================
# КАТАЛОГ
# ==========================================

CATALOG_FILE = "catalog.json"
_catalog_lock = asyncio.Lock()


DEFAULT_CATALOG = {
    "ds": {
        "label": "Discord",
        "emoji": "<:discord:1543647404212093009>",
        "banner": BANNER_STORE_DS,
        "description": "Услуги, связанные с серверами и ботами.",
        "products": [
            {
                "name": "Создание сервера",
                "price": "от 25⭐ / 40₽",
                "description": "Полная настройка сервера под ключ."
            },
            {
                "name": "Создание сервера + настройка ботов",
                "price": "от 25⭐ / 40₽",
                "description": "Сервер и базовая настройка ботов."
            },
            {
                "name": "Создание сервера с кастомным ботом",
                "price": "от 50⭐ / 100₽",
                "description": "Сервер + уникальный бот под ваши задачи."
            },
            {
                "name": "Создание ботов под задачи + хостинг",
                "price": "от 50⭐ / 100₽",
                "description": "Индивидуальная разработка бота с хостингом."
            },
            {
                "name": "Хостинг вашего бота",
                "price": "25⭐ / 50₽ мес.",
                "description": "Ежемесячный хостинг для уже готового бота."
            }
        ]
    },

    "boost": {
        "label": "Накрутка DS",
        "emoji": "<:people:1543647540426055712>",
        "banner": BANNER_STORE_BOOST,
        "description": (
            "Накрутка участников для вашего сервера "
            "(заказ от 50 участников)."
        ),
        "products": [
            {
                "name": "Оффлайн участник",
                "price": "0.25₽",
                "description": "1 оффлайн-участник на сервер."
            },
            {
                "name": "Онлайн участник",
                "price": "0.50₽",
                "description": "1 онлайн-участник на сервер."
            }
        ]
    },

    "steam": {
        "label": "Steam",
        "emoji": "<:steam:1543647341129629756>",
        "banner": BANNER_STORE_STEAM,
        "description": "Пополнение баланса Steam.",
        "products": [
            {
                "name": "Пополнение баланса",
                "price": "1 руб. = 1.02 руб. на баланс",
                "description": "Курс пополнения Steam-кошелька."
            }
        ]
    }
}


# Старые custom_id категорий
CATEGORY_CUSTOM_IDS = {
    "ds": "btn_store_ds",
    "boost": "btn_store_boost",
    "steam": "btn_store_steam"
}


def _save_catalog_sync(data: dict) -> None:
    """Синхронное сохранение каталога."""

    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def _ensure_catalog_file() -> None:
    """Создаёт catalog.json, если его нет."""

    if not os.path.exists(CATALOG_FILE):
        _save_catalog_sync(DEFAULT_CATALOG)


def load_catalog() -> dict:
    """Загрузка каталога."""

    _ensure_catalog_file()

    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, FileNotFoundError):
        _save_catalog_sync(DEFAULT_CATALOG)
        return json.loads(json.dumps(DEFAULT_CATALOG))


async def save_catalog(data: dict) -> None:
    """Безопасное сохранение каталога."""

    async with _catalog_lock:
        _save_catalog_sync(data)


def build_product_fields(products: list) -> list:
    """Формирует поля Embed с товарами."""

    if not products:
        return [
            (
                "🛍️ Товары",
                "Пока нет товаров в этой категории."
            )
        ]

    fields = []
    chunk = ""
    part = 1

    for product in products:

        entry = (
            f"**{product.get('name', 'Без названия')}**\n"
            f"> 💰 Цена: {product.get('price', 'уточняйте')}\n"
            f"> 📝 {product.get('description', 'Без описания')}\n\n"
        )

        if len(chunk) + len(entry) > 1000:

            title = (
                "🛍️ Товары"
                if part == 1
                else f"🛍️ Товары ({part})"
            )

            fields.append(
                (
                    title,
                    chunk.strip()
                )
            )

            chunk = ""
            part += 1

        chunk += entry

    if chunk:

        title = (
            "🛍️ Товары"
            if part == 1
            else f"🛍️ Товары ({part})"
        )

        fields.append(
            (
                title,
                chunk.strip()
            )
        )

    return fields


# ==========================================
# 1. МОДАЛЬНЫЕ ОКНА
# ==========================================

class OrderModal(disnake.ui.Modal):

    def __init__(self):

        components = [

            disnake.ui.TextInput(
                label="Какой товар?",
                placeholder="Например: Создание сервера + бот",
                custom_id="order_item",
                style=disnake.TextInputStyle.short,
                max_length=100
            ),

            disnake.ui.TextInput(
                label="Способ оплаты",
                placeholder="Звёзды / Рубли / СБП / Карта",
                custom_id="order_payment",
                style=disnake.TextInputStyle.short,
                max_length=50
            ),

            disnake.ui.TextInput(
                label="Комментарий к заказу",
                placeholder="Опишите ваши пожелания...",
                custom_id="order_details",
                style=disnake.TextInputStyle.paragraph,
                required=False,
                max_length=1000
            )
        ]

        super().__init__(
            title="Оформление заказа",
            custom_id="modal_order",
            components=components
        )

    async def callback(
        self,
        inter: disnake.ModalInteraction
    ):

        await inter.response.defer(ephemeral=True)

        guild = inter.guild

        category = guild.get_channel(
            CATEGORY_TICKETS_ID
        )

        staff_role = guild.get_role(
            STAFF_ROLE_ID
        )

        overwrites = {
            guild.default_role:
                disnake.PermissionOverwrite(
                    read_messages=False
                ),

            inter.author:
                disnake.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )
        }

        if staff_role:

            overwrites[staff_role] = (
                disnake.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )
            )

        ticket_channel = await guild.create_text_channel(
            name=f"заказ-{inter.author.name}",
            category=category,
            overwrites=overwrites
        )

        item = inter.text_values["order_item"]
        payment = inter.text_values["order_payment"]
        details = (
            inter.text_values["order_details"]
            or "Не указано"
        )

        embed = disnake.Embed(
            title="🛒 Новый заказ!",
            description=(
                f"Пользователь {inter.author.mention} "
                "создал заказ."
            ),
            color=disnake.Color.green()
        )

        embed.add_field(
            name="📦 Товар",
            value=f"```\n{item}\n```",
            inline=False
        )

        embed.add_field(
            name="💳 Способ оплаты",
            value=f"```\n{payment}\n```",
            inline=False
        )

        embed.add_field(
            name="📝 Детали",
            value=f"```\n{details}\n```",
            inline=False
        )

        await ticket_channel.send(
            content=(
                f"{inter.author.mention} "
                f"{staff_role.mention if staff_role else ''}"
            ),
            embed=embed,
            view=CloseTicketView()
        )

        await inter.edit_original_message(
            content=(
                "✅ Ваш заказ успешно создан: "
                f"{ticket_channel.mention}"
            )
        )


class SupportModal(disnake.ui.Modal):

    def __init__(self):

        components = [

            disnake.ui.TextInput(
                label="Причина обращения",
                placeholder="Опишите проблему или вопрос...",
                custom_id="support_reason",
                style=disnake.TextInputStyle.paragraph,
                max_length=1000
            )
        ]

        super().__init__(
            title="Обращение в поддержку",
            custom_id="modal_support",
            components=components
        )

    async def callback(
        self,
        inter: disnake.ModalInteraction
    ):

        await inter.response.defer(ephemeral=True)

        guild = inter.guild

        category = guild.get_channel(
            CATEGORY_TICKETS_ID
        )

        staff_role = guild.get_role(
            STAFF_ROLE_ID
        )

        overwrites = {
            guild.default_role:
                disnake.PermissionOverwrite(
                    read_messages=False
                ),

            inter.author:
                disnake.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )
        }

        if staff_role:

            overwrites[staff_role] = (
                disnake.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )
            )

        ticket_channel = await guild.create_text_channel(
            name=f"тикет-{inter.author.name}",
            category=category,
            overwrites=overwrites
        )

        reason = inter.text_values["support_reason"]

        embed = disnake.Embed(
            title="🛠️ Новое обращение в поддержку",
            description=(
                f"Пользователь {inter.author.mention} "
                "обратился за помощью."
            ),
            color=disnake.Color.orange()
        )

        embed.add_field(
            name="❓ Причина обращения",
            value=f"```\n{reason}\n```",
            inline=False
        )

        await ticket_channel.send(
            content=(
                f"{inter.author.mention} "
                f"{staff_role.mention if staff_role else ''}"
            ),
            embed=embed,
            view=CloseTicketView()
        )

        await inter.edit_original_message(
            content=(
                "✅ Тикет поддержки создан: "
                f"{ticket_channel.mention}"
            )
        )


class StaffModal(disnake.ui.Modal):

    def __init__(self, role_name: str):

        self.role_name = role_name

        components = [

            disnake.ui.TextInput(
                label="Ваше имя и возраст",
                placeholder="Александр, 17 лет",
                custom_id="staff_age",
                style=disnake.TextInputStyle.short
            ),

            disnake.ui.TextInput(
                label="Сколько времени уделять?",
                placeholder="3-4 часа в день",
                custom_id="staff_time",
                style=disnake.TextInputStyle.short
            ),

            disnake.ui.TextInput(
                label="Опыт на похожей должности",
                placeholder="Опишите ваш опыт...",
                custom_id="staff_experience",
                style=disnake.TextInputStyle.paragraph
            )
        ]

        super().__init__(
            title=f"Анкета: {role_name}"[:45],
            custom_id="modal_staff",
            components=components
        )

    async def callback(
        self,
        inter: disnake.ModalInteraction
    ):

        await inter.response.defer(ephemeral=True)

        log_channel = inter.guild.get_channel(
            STAFF_LOG_CHANNEL_ID
        )

        embed = disnake.Embed(
            title=(
                f"📥 Новая заявка: "
                f"{self.role_name}"
            ),
            color=disnake.Color.blue(),
            timestamp=inter.created_at
        )

        embed.set_author(
            name=inter.author.display_name,
            icon_url=inter.author.display_avatar.url
        )

        embed.add_field(
            name="👤 Кандидат",
            value=inter.author.mention,
            inline=True
        )

        embed.add_field(
            name="🆔 ID",
            value=f"`{inter.author.id}`",
            inline=True
        )

        embed.add_field(
            name="📌 Должность",
            value=f"`{self.role_name}`",
            inline=False
        )

        embed.add_field(
            name="🔞 Имя и возраст",
            value=inter.text_values["staff_age"],
            inline=False
        )

        embed.add_field(
            name="⏰ Актив",
            value=inter.text_values["staff_time"],
            inline=False
        )

        embed.add_field(
            name="💼 Опыт",
            value=inter.text_values["staff_experience"],
            inline=False
        )

        if log_channel:

            view = StaffReviewView(
                applicant_id=inter.author.id,
                role_name=self.role_name
            )

            await log_channel.send(
                embed=embed,
                view=view
            )

        await inter.edit_original_message(
            content="✅ Ваша заявка отправлена на рассмотрение!"
        )


class StaffRejectModal(disnake.ui.Modal):

    def __init__(
        self,
        applicant: disnake.Member,
        role_name: str
    ):

        self.applicant = applicant
        self.role_name = role_name

        components = [

            disnake.ui.TextInput(
                label="Причина отказа",
                placeholder="Например: Не подходите по требованиям",
                custom_id="reject_reason",
                style=disnake.TextInputStyle.paragraph,
                max_length=500
            )
        ]

        super().__init__(
            title="Отказ в заявке",
            custom_id="modal_staff_reject",
            components=components
        )

    async def callback(
        self,
        inter: disnake.ModalInteraction
    ):

        await inter.response.defer()

        reason = inter.text_values[
            "reject_reason"
        ]

        embed = inter.message.embeds[0]

        embed.color = disnake.Color.red()

        embed.add_field(
            name="❌ Статус",
            value=(
                f"Отклонено администратором "
                f"{inter.author.mention}\n"
                f"**Причина:** {reason}"
            ),
            inline=False
        )

        view = disnake.ui.View.from_message(
            inter.message
        )

        for child in view.children:
            child.disabled = True

        await inter.edit_original_message(
            embed=embed,
            view=view
        )

        try:

            await self.applicant.send(
                f"❌ Ваша заявка на должность "
                f"**{self.role_name}** была отклонена.\n"
                f"**Причина:** {reason}"
            )

        except disnake.Forbidden:
            pass


# ==========================================
# 1.1 УПРАВЛЕНИЕ МАГАЗИНОМ
# ==========================================

class CategorySettingsModal(disnake.ui.Modal):

    def __init__(
        self,
        cat_id: str,
        cat_data: dict
    ):

        self.cat_id = cat_id

        components = [

            disnake.ui.TextInput(
                label="Название категории",
                custom_id="cat_label",
                style=disnake.TextInputStyle.short,
                value=cat_data.get(
                    "label",
                    ""
                ) or "",
                max_length=80
            ),

            disnake.ui.TextInput(
                label="Эмодзи",
                placeholder="Например: 🔥 или <:name:id>",
                custom_id="cat_emoji",
                style=disnake.TextInputStyle.short,
                value=cat_data.get(
                    "emoji",
                    ""
                ) or "",
                required=False,
                max_length=100
            ),

            disnake.ui.TextInput(
                label="Описание категории",
                custom_id="cat_description",
                style=disnake.TextInputStyle.paragraph,
                value=cat_data.get(
                    "description",
                    ""
                ) or "",
                required=False,
                max_length=1000
            ),

            disnake.ui.TextInput(
                label="Ссылка на баннер",
                placeholder="https://...",
                custom_id="cat_banner",
                style=disnake.TextInputStyle.short,
                value=cat_data.get(
                    "banner",
                    ""
                ) or "",
                required=False,
                max_length=500
            )
        ]

        super().__init__(
            title=f"Настройка: {cat_id}"[:45],
            custom_id=f"modal_cat_settings_{cat_id}",
            components=components
        )

    async def callback(
        self,
        inter: disnake.ModalInteraction
    ):

        await inter.response.defer(
            ephemeral=True
        )

        catalog = load_catalog()

        if self.cat_id not in catalog:

            await inter.edit_original_message(
                content=(
                    "❌ Категория была удалена, "
                    "действие отменено."
                )
            )

            return

        catalog[self.cat_id]["label"] = (
            inter.text_values["cat_label"]
        )

        catalog[self.cat_id]["emoji"] = (
            inter.text_values["cat_emoji"]
            or None
        )

        catalog[self.cat_id]["description"] = (
            inter.text_values["cat_description"]
        )

        catalog[self.cat_id]["banner"] = (
            inter.text_values["cat_banner"]
        )

        await save_catalog(catalog)

        await inter.edit_original_message(
            content=(
                f"✅ Категория "
                f"**{catalog[self.cat_id]['label']}** "
                "обновлена.\n"
                "ℹ️ Чтобы изменения появились на витрине, "
                "повторно отправьте меню через `/setup`."
            )
        )


class AddProductModal(disnake.ui.Modal):

    def __init__(self, cat_id: str):

        self.cat_id = cat_id

        components = [

            disnake.ui.TextInput(
                label="Название товара",
                custom_id="p_name",
                style=disnake.TextInputStyle.short,
                max_length=100
            ),

            disnake.ui.TextInput(
                label="Цена",
                custom_id="p_price",
                style=disnake.TextInputStyle.short,
                max_length=100
            ),

            disnake.ui.TextInput(
                label="Описание",
                custom_id="p_desc",
                style=disnake.TextInputStyle.paragraph,
                required=False,
                max_length=300
            )
        ]

        super().__init__(
            title="Добавить товар",
            custom_id=f"modal_add_product_{cat_id}",
            components=components
        )

    async def callback(
        self,
        inter: disnake.ModalInteraction
    ):

        await inter.response.defer(
            ephemeral=True
        )

        catalog = load_catalog()

        if self.cat_id not in catalog:

            await inter.edit_original_message(
                content="❌ Категория не найдена."
            )

            return

        product = {
            "name": inter.text_values["p_name"],
            "price": inter.text_values["p_price"],
            "description": (
                inter.text_values["p_desc"]
                or "Без описания"
            )
        }

        catalog[self.cat_id].setdefault(
            "products",
            []
        ).append(product)

        await save_catalog(catalog)

        await inter.edit_original_message(
            content=(
                f"✅ Товар **{product['name']}** "
                f"добавлен в категорию "
                f"**{catalog[self.cat_id].get('label', self.cat_id)}**."
            )
        )


class EditProductModal(disnake.ui.Modal):

    def __init__(
        self,
        cat_id: str,
        index: int,
        product: dict
    ):

        self.cat_id = cat_id
        self.index = index

        components = [

            disnake.ui.TextInput(
                label="Название товара",
                custom_id="p_name",
                style=disnake.TextInputStyle.short,
                value=product.get(
                    "name",
                    ""
                ),
                max_length=100
            ),

            disnake.ui.TextInput(
                label="Цена",
                custom_id="p_price",
                style=disnake.TextInputStyle.short,
                value=product.get(
                    "price",
                    ""
                ),
                max_length=100
            ),

            disnake.ui.TextInput(
                label="Описание",
                custom_id="p_desc",
                style=disnake.TextInputStyle.paragraph,
                value=product.get(
                    "description",
                    ""
                ),
                required=False,
                max_length=300
            )
        ]

        super().__init__(
            title="Редактировать товар",
            custom_id=(
                f"modal_edit_product_"
                f"{cat_id}_{index}"
            ),
            components=components
        )

    async def callback(
        self,
        inter: disnake.ModalInteraction
    ):

        await inter.response.defer(
            ephemeral=True
        )

        catalog = load_catalog()

        products = catalog.get(
            self.cat_id,
            {}
        ).get(
            "products",
            []
        )

        if self.index >= len(products):

            await inter.edit_original_message(
                content=(
                    "❌ Товар не найден "
                    "(возможно, был удалён)."
                )
            )

            return

        products[self.index] = {
            "name": inter.text_values["p_name"],
            "price": inter.text_values["p_price"],
            "description": (
                inter.text_values["p_desc"]
                or "Без описания"
            )
        }

        await save_catalog(catalog)

        await inter.edit_original_message(
            content="✅ Товар успешно обновлён."
        )


# ==========================================
# НОВАЯ КАТЕГОРИЯ
# ==========================================

class AddCategoryModal(disnake.ui.Modal):
    """
    Создание новой категории.

    ВАЖНО:
    Discord разрешает label TextInput максимум 45 символов.
    Поэтому здесь используются короткие label.
    """

    def __init__(self):

        components = [

            disnake.ui.TextInput(
                label="ID категории",
                placeholder="Например: minecraft",
                custom_id="new_cat_id",
                style=disnake.TextInputStyle.short,
                max_length=40
            ),

            disnake.ui.TextInput(
                label="Название категории",
                placeholder="Например: Minecraft",
                custom_id="new_cat_label",
                style=disnake.TextInputStyle.short,
                max_length=80
            ),

            disnake.ui.TextInput(
                label="Эмодзи",
                placeholder="Необязательно: 🔥",
                custom_id="new_cat_emoji",
                style=disnake.TextInputStyle.short,
                required=False,
                max_length=100
            ),

            disnake.ui.TextInput(
                label="Описание категории",
                placeholder="Краткое описание категории",
                custom_id="new_cat_description",
                style=disnake.TextInputStyle.paragraph,
                required=False,
                max_length=1000
            )
        ]

        super().__init__(
            title="Новая категория",
            custom_id="modal_add_category",
            components=components
        )

    async def callback(
        self,
        inter: disnake.ModalInteraction
    ):

        await inter.response.defer(
            ephemeral=True
        )

        catalog = load_catalog()

        raw_id = (
            inter.text_values["new_cat_id"]
            .strip()
            .lower()
        )

        # Разрешаем только буквы, цифры и "_"
        cat_id = "".join(
            ch
            for ch in raw_id
            if ch.isalnum() or ch == "_"
        )

        if not cat_id:

            await inter.edit_original_message(
                content=(
                    "❌ Некорректный ID категории.\n"
                    "Используйте латинские буквы, "
                    "цифры и `_`."
                )
            )

            return

        if cat_id in catalog:

            await inter.edit_original_message(
                content=(
                    "❌ Категория с таким ID "
                    "уже существует."
                )
            )

            return

        label = (
            inter.text_values["new_cat_label"]
            .strip()
        )

        emoji = (
            inter.text_values["new_cat_emoji"]
            .strip()
        )

        description = (
            inter.text_values["new_cat_description"]
            .strip()
        )

        if not label:

            await inter.edit_original_message(
                content=(
                    "❌ Название категории "
                    "не может быть пустым."
                )
            )

            return

        catalog[cat_id] = {
            "label": label,
            "emoji": emoji or None,
            "banner": "",
            "description": description,
            "products": []
        }

        await save_catalog(catalog)

        await inter.edit_original_message(
            content=(
                f"✅ Категория **{label}** создана.\n"
                "ℹ️ Отправьте меню магазина заново "
                "через `/setup`, чтобы кнопка появилась "
                "на витрине."
            )
        )


# ==========================================
# 2. VIEWS
# ==========================================

class CloseTicketView(disnake.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @disnake.ui.button(
        label="Закрыть тикет",
        style=disnake.ButtonStyle.danger,
        emoji="🔒",
        custom_id="close_ticket_btn"
    )
    async def close_ticket(
        self,
        button: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ):

        await inter.response.send_message(
            "🔒 Канал будет удален через 5 секунд..."
        )

        await asyncio.sleep(5)

        await inter.channel.delete()


class StaffReviewView(disnake.ui.View):

    def __init__(
        self,
        applicant_id: int,
        role_name: str
    ):

        super().__init__(
            timeout=None
        )

        self.applicant_id = applicant_id
        self.role_name = role_name

    @disnake.ui.button(
        label="Одобрить",
        style=disnake.ButtonStyle.success,
        emoji="✅",
        custom_id="btn_staff_accept"
    )
    async def accept(
        self,
        button: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ):

        guild = inter.guild

        applicant = guild.get_member(
            self.applicant_id
        )

        if not applicant:

            await inter.response.send_message(
                "❌ Кандидат не найден на сервере!",
                ephemeral=True
            )

            return

        staff_role = guild.get_role(
            STAFF_ROLE_ID
        )

        if staff_role:

            await applicant.add_roles(
                staff_role,
                reason=(
                    f"Заявка одобрена "
                    f"администратором {inter.author}"
                )
            )

        embed = inter.message.embeds[0]

        embed.color = disnake.Color.green()

        embed.add_field(
            name="✅ Статус",
            value=(
                f"Одобрено администратором "
                f"{inter.author.mention}"
            ),
            inline=False
        )

        for child in self.children:
            child.disabled = True

        await inter.response.edit_message(
            embed=embed,
            view=self
        )

        try:

            await applicant.send(
                f"🎉 Поздравляем! "
                f"Ваша заявка на должность "
                f"**{self.role_name}** одобрена."
            )

        except disnake.Forbidden:
            pass

    @disnake.ui.button(
        label="Отклонить",
        style=disnake.ButtonStyle.danger,
        emoji="❌",
        custom_id="btn_staff_reject"
    )
    async def reject(
        self,
        button: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ):

        guild = inter.guild

        applicant = guild.get_member(
            self.applicant_id
        )

        if not applicant:

            await inter.response.send_message(
                "❌ Кандидат не найден на сервере!",
                ephemeral=True
            )

            return

        await inter.response.send_modal(
            StaffRejectModal(
                applicant=applicant,
                role_name=self.role_name
            )
        )


class OrderActionView(disnake.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @disnake.ui.button(
        label="Сделать заказ",
        style=disnake.ButtonStyle.success,
        emoji="<:shop:1543647510634045490>",
        custom_id="btn_make_order"
    )
    async def make_order(
        self,
        button: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ):

        await inter.response.send_modal(
            OrderModal()
        )


# ==========================================
# ВИТРИНА МАГАЗИНА
# ==========================================

class CategoryButton(disnake.ui.Button):

    def __init__(
        self,
        cat_id: str,
        cat_data: dict
    ):

        custom_id = CATEGORY_CUSTOM_IDS.get(
            cat_id,
            f"btn_store_cat_{cat_id}"
        )

        super().__init__(
            label=cat_data.get(
                "label",
                cat_id
            )[:80],

            style=disnake.ButtonStyle.secondary,

            emoji=cat_data.get(
                "emoji"
            ) or None,

            custom_id=custom_id
        )

        self.cat_id = cat_id

    async def callback(
        self,
        inter: disnake.MessageInteraction
    ):

        catalog = load_catalog()

        cat_data = catalog.get(
            self.cat_id
        )

        if not cat_data:

            await inter.response.send_message(
                "❌ Эта категория больше не существует.",
                ephemeral=True
            )

            return

        embed = disnake.Embed(
            title=cat_data.get(
                "label",
                self.cat_id
            ),

            description=(
                cat_data.get("description")
                or "\u200b"
            ),

            color=0x2B2D31
        )

        if cat_data.get("banner"):

            embed.set_image(
                url=cat_data["banner"]
            )

        for name, value in build_product_fields(
            cat_data.get(
                "products",
                []
            )
        ):

            embed.add_field(
                name=name,
                value=value,
                inline=False
            )

        await inter.response.send_message(
            embed=embed,
            view=OrderActionView(),
            ephemeral=True
        )


class DynamicStoreView(disnake.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        catalog = load_catalog()

        for cat_id, cat_data in catalog.items():

            self.add_item(
                CategoryButton(
                    cat_id,
                    cat_data
                )
            )


# ==========================================
# АДМИН-ПАНЕЛЬ МАГАЗИНА
# ==========================================

class ProductSelect(disnake.ui.StringSelect):

    def __init__(
        self,
        cat_id: str,
        options: list,
        action: str
    ):

        placeholder = (
            "Выберите товар для редактирования"
            if action == "edit"
            else "Выберите товар для удаления"
        )

        super().__init__(
            placeholder=placeholder,
            options=options,
            custom_id=(
                f"shop_admin_select_product_"
                f"{action}_{cat_id}"
            )
        )

        self.cat_id = cat_id
        self.action = action

    async def callback(
        self,
        inter: disnake.MessageInteraction
    ):

        index = int(
            self.values[0]
        )

        catalog = load_catalog()

        products = catalog.get(
            self.cat_id,
            {}
        ).get(
            "products",
            []
        )

        if index >= len(products):

            await inter.response.send_message(
                "❌ Товар не найден "
                "(список мог измениться).",
                ephemeral=True
            )

            return

        if self.action == "edit":

            await inter.response.send_modal(
                EditProductModal(
                    self.cat_id,
                    index,
                    products[index]
                )
            )

        else:

            removed = products.pop(index)

            await save_catalog(catalog)

            await inter.response.edit_message(
                content=(
                    f"🗑️ Товар "
                    f"**{removed['name']}** удалён."
                ),
                view=None
            )


class ProductSelectView(disnake.ui.View):

    def __init__(
        self,
        cat_id: str,
        products: list,
        action: str
    ):

        super().__init__(
            timeout=180
        )

        options = [

            disnake.SelectOption(
                label=product.get(
                    "name",
                    "Без названия"
                )[:100],

                value=str(index),

                description=(
                    product.get(
                        "price",
                        ""
                    )[:100]
                    or None
                )
            )

            for index, product
            in enumerate(products)
        ][:25]

        self.add_item(
            ProductSelect(
                cat_id,
                options,
                action
            )
        )


class ShopCategoryActionView(disnake.ui.View):

    def __init__(self, cat_id: str):

        super().__init__(
            timeout=180
        )

        self.cat_id = cat_id

    @disnake.ui.button(
        label="Настройки категории",
        style=disnake.ButtonStyle.primary,
        emoji="⚙️"
    )
    async def edit_category(
        self,
        button: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ):

        catalog = load_catalog()

        cat_data = catalog.get(
            self.cat_id
        )

        if not cat_data:

            await inter.response.send_message(
                "❌ Категория не найдена.",
                ephemeral=True
            )

            return

        await inter.response.send_modal(
            CategorySettingsModal(
                self.cat_id,
                cat_data
            )
        )

    @disnake.ui.button(
        label="Добавить товар",
        style=disnake.ButtonStyle.success,
        emoji="➕"
    )
    async def add_product(
        self,
        button: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ):

        await inter.response.send_modal(
            AddProductModal(
                self.cat_id
            )
        )

    @disnake.ui.button(
        label="Редактировать товар",
        style=disnake.ButtonStyle.secondary,
        emoji="✏️"
    )
    async def edit_product(
        self,
        button: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ):

        catalog = load_catalog()

        products = catalog.get(
            self.cat_id,
            {}
        ).get(
            "products",
            []
        )

        if not products:

            await inter.response.send_message(
                "❌ В этой категории пока нет товаров.",
                ephemeral=True
            )

            return

        await inter.response.send_message(
            "Выберите товар для редактирования:",

            view=ProductSelectView(
                self.cat_id,
                products,
                action="edit"
            ),

            ephemeral=True
        )

    @disnake.ui.button(
        label="Удалить товар",
        style=disnake.ButtonStyle.danger,
        emoji="🗑️"
    )
    async def delete_product(
        self,
        button: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ):

        catalog = load_catalog()

        products = catalog.get(
            self.cat_id,
            {}
        ).get(
            "products",
            []
        )

        if not products:

            await inter.response.send_message(
                "❌ В этой категории пока нет товаров.",
                ephemeral=True
            )

            return

        await inter.response.send_message(
            "Выберите товар для удаления:",

            view=ProductSelectView(
                self.cat_id,
                products,
                action="delete"
            ),

            ephemeral=True
        )


class ShopCategorySelect(disnake.ui.StringSelect):

    def __init__(self, options: list):

        super().__init__(
            placeholder="Выберите категорию",
            options=options,
            custom_id="shop_admin_select_category"
        )

    async def callback(
        self,
        inter: disnake.MessageInteraction
    ):

        cat_id = self.values[0]

        if cat_id == "__none__":

            await inter.response.send_message(
                "❌ В каталоге пока нет категорий. "
                "Добавьте новую кнопкой ниже.",
                ephemeral=True
            )

            return

        catalog = load_catalog()

        cat_data = catalog.get(
            cat_id
        )

        if not cat_data:

            await inter.response.send_message(
                "❌ Категория не найдена.",
                ephemeral=True
            )

            return

        embed = disnake.Embed(
            title=(
                "⚙️ Управление категорией: "
                f"{cat_data.get('label', cat_id)}"
            ),

            description=(
                "Товаров в категории: "
                f"**{len(cat_data.get('products', []))}**"
            ),

            color=0x2B2D31
        )

        await inter.response.send_message(
            embed=embed,
            view=ShopCategoryActionView(cat_id),
            ephemeral=True
        )


class AddCategoryButton(disnake.ui.Button):

    def __init__(self):

        super().__init__(
            label="Новая категория",
            style=disnake.ButtonStyle.success,
            emoji="➕",
            custom_id="shop_admin_add_category"
        )

    async def callback(
        self,
        inter: disnake.MessageInteraction
    ):

        await inter.response.send_modal(
            AddCategoryModal()
        )


class ShopCategorySelectView(disnake.ui.View):

    def __init__(self):

        super().__init__(
            timeout=180
        )

        catalog = load_catalog()

        if catalog:

            options = [

                disnake.SelectOption(
                    label=data.get(
                        "label",
                        cid
                    )[:100],

                    value=cid,

                    description=(
                        f"Товаров: "
                        f"{len(data.get('products', []))}"
                    )[:100]
                )

                for cid, data
                in catalog.items()
            ][:25]

        else:

            options = [
                disnake.SelectOption(
                    label="Нет категорий",
                    value="__none__"
                )
            ]

        self.add_item(
            ShopCategorySelect(options)
        )

        self.add_item(
            AddCategoryButton()
        )


# ==========================================
# STAFF
# ==========================================

class StaffSelectView(disnake.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @disnake.ui.string_select(
        placeholder="Выбери роль",
        custom_id="select_staff_role",
        options=[

            disnake.SelectOption(
                label="Trainee",
                value="Trainee",
                description="Стажер сервера",
                emoji="<:staff:1543647456196042932>"
            ),

            disnake.SelectOption(
                label="Moderator",
                value="Moderator",
                description="Модератор чатов",
                emoji="<:staff:1543647456196042932>"
            ),

            disnake.SelectOption(
                label="Support",
                value="Support",
                description="Агент поддержки",
                emoji="<:support:1543647293494796318>"
            )
        ]
    )
    async def select_callback(
        self,
        select: disnake.ui.StringSelect,
        inter: disnake.MessageInteraction
    ):

        selected_role = select.values[0]

        await inter.response.send_modal(
            StaffModal(
                role_name=selected_role
            )
        )


class SupportView(disnake.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @disnake.ui.button(
        label="Открыть тикет",
        style=disnake.ButtonStyle.primary,
        emoji="<:support:1543647293494796318>",
        custom_id="btn_open_support"
    )
    async def open_support(
        self,
        button: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ):

        await inter.response.send_modal(
            SupportModal()
        )


# ==========================================
# /SETUP
# ==========================================

@bot.slash_command(
    name="setup",
    description=(
        "Настройка и отправка системных меню"
    ),
    default_member_permissions=disnake.Permissions(
        administrator=True
    )
)
@commands.has_permissions(
    administrator=True
)
async def setup(
    inter: disnake.ApplicationCommandInteraction,

    menu_type: str = commands.Param(
        name="меню",
        description="Выберите какое меню отправить",
        choices={
            "Витрина / Магазин": "store",
            "Набор в Стафф": "staff",
            "Поддержка": "support"
        }
    )
):

    if menu_type == "store":

        catalog = load_catalog()

        lines = []

        for cid, data in catalog.items():

            emoji = data.get(
                "emoji"
            ) or ""

            label = data.get(
                "label",
                cid
            )

            desc = data.get(
                "description"
            ) or ""

            lines.append(
                f"• {emoji} **{label}** — {desc}".strip()
            )

        description = (
            "Выберите интересующую вас категорию "
            "и воспользуйтесь кнопкой ниже, "
            "чтобы ознакомиться с ценами.\n\n"
            + "\n".join(lines)
        )

        embed = disnake.Embed(
            title="👋 Приветствуем в магазине!",
            description=description,
            color=0x2B2D31
        )

        embed.set_image(
            url=BANNER_STORE_MAIN
        )

        await inter.channel.send(
            embed=embed,
            view=DynamicStoreView()
        )

        await inter.response.send_message(
            "✅ Меню магазина успешно отправлено!",
            ephemeral=True
        )

    elif menu_type == "staff":

        embed = disnake.Embed(
            title="Набор в команду",

            description=(
                "Станьте частью команды сервера "
                "и развивайтесь вместе с нами.\n"
                "Выберите должность в меню ниже, "
                "чтобы заполнить анкету.\n\n"

                "**Что от вас требуется:**\n"
                "✦ • Возраст 16+\n"
                "✧ • Минимальный актив в день: 2 часа\n"
                "✦ • Грамотная письменная / устная речь\n"
                "👑 • Желание развиваться и помогать участникам сервера\n\n"

                "**Что вы получите от нас:**\n"
                "✧ • Дружелюбный состав\n"
                "✦ • Опыт в данной сфере\n"
                "✧ • Понятная система повышений\n"
                "👑 • Оплата труда / бонусы"
            ),

            color=0x2B2D31
        )

        embed.set_image(
            url=BANNER_STAFF
        )

        embed.set_footer(
            text="Recruitment System"
        )

        await inter.channel.send(
            embed=embed,
            view=StaffSelectView()
        )

        await inter.response.send_message(
            "✅ Меню набора успешно отправлено!",
            ephemeral=True
        )

    elif menu_type == "support":

        embed = disnake.Embed(
            title="🎧 Центр Поддержки",

            description=(
                "Возникли вопросы или проблемы? "
                "Нажмите кнопку ниже, чтобы "
                "связаться с администрацией."
            ),

            color=0x2B2D31
        )

        embed.set_image(
            url=BANNER_SUPPORT
        )

        await inter.channel.send(
            embed=embed,
            view=SupportView()
        )

        await inter.response.send_message(
            "✅ Меню поддержки успешно отправлено!",
            ephemeral=True
        )


# ==========================================
# /SHOP
# ==========================================

@bot.slash_command(
    name="shop",
    description=(
        "Управление категориями и товарами магазина"
    ),
    default_member_permissions=disnake.Permissions(
        administrator=True
    )
)
@commands.has_permissions(
    administrator=True
)
async def shop(
    inter: disnake.ApplicationCommandInteraction
):

    catalog = load_catalog()

    embed = disnake.Embed(
        title="🛠️ Управление магазином",

        description=(
            f"Всего категорий: **{len(catalog)}**\n"
            "Выберите категорию ниже, чтобы изменить "
            "её оформление или список товаров, "
            "либо создайте новую категорию."
        ),

        color=0x2B2D31
    )

    await inter.response.send_message(
        embed=embed,
        view=ShopCategorySelectView(),
        ephemeral=True
    )


# ==========================================
# СЧЁТЧИК УЧАСТНИКОВ
# ==========================================

_counter_dirty = False


def _mark_counter_dirty():

    global _counter_dirty

    _counter_dirty = True


async def _apply_counter_update():

    global _counter_dirty

    if not COUNTER_CHANNEL_ID:
        return

    for guild in bot.guilds:

        channel = guild.get_channel(
            COUNTER_CHANNEL_ID
        )

        if channel is None:
            continue

        new_name = (
            f"👥 Участников: "
            f"{guild.member_count}"
        )

        if channel.name == new_name:
            continue

        try:

            await channel.edit(
                name=new_name
            )

        except disnake.HTTPException as error:

            print(
                "⚠️ Не удалось обновить "
                f"канал-счётчик: {error}"
            )

    _counter_dirty = False


@tasks.loop(minutes=10)
async def update_counter_loop():

    if _counter_dirty:

        await _apply_counter_update()


@update_counter_loop.before_loop
async def before_update_counter_loop():

    await bot.wait_until_ready()


@bot.event
async def on_member_join(
    member: disnake.Member
):

    _mark_counter_dirty()


@bot.event
async def on_member_remove(
    member: disnake.Member
):

    _mark_counter_dirty()


# ==========================================
# READY
# ==========================================

@bot.event
async def on_ready():

    print(
        f"Бот {bot.user} успешно запущен!"
    )

    # Persistent views
    bot.add_view(
        DynamicStoreView()
    )

    bot.add_view(
        OrderActionView()
    )

    bot.add_view(
        StaffSelectView()
    )

    bot.add_view(
        SupportView()
    )

    bot.add_view(
        CloseTicketView()
    )

    _mark_counter_dirty()

    if not update_counter_loop.is_running():

        update_counter_loop.start()


# ==========================================
# ЗАПУСК
# ==========================================

TOKEN = os.getenv("TOKEN")

if not TOKEN:

    print(
        "❌ Ошибка: переменная окружения TOKEN "
        "не найдена!"
    )

    print(
        "Укажите TOKEN в панели управления хостингом."
    )

else:

    bot.run(TOKEN)import os
import json
import asyncio

import disnake
from disnake.ext import commands, tasks

# ==========================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ==========================================
intents = disnake.Intents.default()
intents.message_content = True
# Intent "members" обязателен для on_member_join / on_member_remove
# и для корректного значения guild.member_count.
# Не забудьте включить "SERVER MEMBERS INTENT" в Discord Developer Portal!
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# ID И НАСТРОЙКИ (Установлены твои ID)
# ==========================================
CATEGORY_TICKETS_ID = 1543635533375475833      # Категория, где будут создаваться тикеты
STAFF_LOG_CHANNEL_ID = 1543652454229352448     # Канал для заявок на стафф
STAFF_ROLE_ID = 1543621903539769344            # Роль персонала для доступа к тикетам

# ID голосового канала-счётчика участников сервера.
# Замените 0 на реальный ID вашего голосового канала!
# Название канала будет автоматически обновляться вида: "👥 Участников: 125"
COUNTER_CHANNEL_ID = 1550279189582848102

# Ссылки на баннеры
BANNER_STORE_MAIN = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648642152398948/Picsart_26-08-30_18-18-35-370.png?ex=6a95a253&is=6a9450d3&hm=7bae522765c81430084201be33cc556a08f3cbf75723ddd8cc19f1137698f03a&"
BANNER_STORE_DS = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648640847970384/Picsart_26-08-30_18-19-53-903.png?ex=6a95a253&is=6a9450d3&hm=1ac98b367169090139e9afebf7a49d5b1aca9cb9cda7c9adf1b9d4eb52aee5ef&"
BANNER_STORE_BOOST = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648640449642598/Picsart_26-08-30_18-20-30-349.png?ex=6a95a253&is=6a9450d3&hm=bf12d034845adf83143a09c3669e0d763e21c681519de3e903be7eda2f3107af&"
BANNER_STORE_STEAM = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648640118030376/Picsart_26-08-30_18-20-41-435.png?ex=6a95a253&is=6a9450d3&hm=e6443560d02e5c4b526feda64d7608ffd4824ff941c89b5a1c81f1a7b60a60b3&"
BANNER_STAFF = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648641636507699/Picsart_26-08-30_18-19-27-501.png?ex=6a95a253&is=6a9450d3&hm=f0a0d1dcb54b36a864465efc2563876cbfc8ff59ccabd83ae483786c98405d23&"
BANNER_SUPPORT = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648641242239056/Picsart_26-08-30_18-19-41-401.png?ex=6a95a253&is=6a9450d3&hm=ba87b21f4140ae240fce10f22365842088c056c1dcadb0e806c874543df12091&"

# ==========================================
# КАТАЛОГ ТОВАРОВ (catalog.json)
# ==========================================
# Структура файла catalog.json:
# {
#     "id_категории": {
#         "label": "Название кнопки",
#         "emoji": "<:emoji:123456789>",
#         "banner": "https://...",
#         "description": "Текст-описание категории",
#         "products": [
#             {"name": "Товар", "price": "100₽", "description": "Описание товара"}
#         ]
#     },
#     ...
# }

CATALOG_FILE = "catalog.json"
_catalog_lock = asyncio.Lock()

# Стартовые данные каталога — переносим текущие цены магазина,
# чтобы после первого запуска ничего не пропало.
DEFAULT_CATALOG = {
    "ds": {
        "label": "Discord",
        "emoji": "<:discord:1543647404212093009>",
        "banner": BANNER_STORE_DS,
        "description": "Услуги, связанные с серверами и ботами.",
        "products": [
            {
                "name": "Создание сервера",
                "price": "от 25⭐ / 40₽",
                "description": "Полная настройка сервера под ключ."
            },
            {
                "name": "Создание сервера + настройка ботов",
                "price": "от 25⭐ / 40₽",
                "description": "Сервер и базовая настройка ботов."
            },
            {
                "name": "Создание сервера с кастомным ботом",
                "price": "от 50⭐ / 100₽",
                "description": "Сервер + уникальный бот под ваши задачи."
            },
            {
                "name": "Создание ботов под задачи + хостинг",
                "price": "от 50⭐ / 100₽",
                "description": "Индивидуальная разработка бота с хостингом."
            },
            {
                "name": "Хостинг вашего бота",
                "price": "25⭐ / 50₽ мес.",
                "description": "Ежемесячный хостинг для уже готового бота."
            }
        ]
    },
    "boost": {
        "label": "Накрутка DS",
        "emoji": "<:people:1543647540426055712>",
        "banner": BANNER_STORE_BOOST,
        "description": "Накрутка участников для вашего сервера (заказ от 50 участников).",
        "products": [
            {
                "name": "Оффлайн участник",
                "price": "0.25₽",
                "description": "1 оффлайн-участник на сервер."
            },
            {
                "name": "Онлайн участник",
                "price": "0.50₽",
                "description": "1 онлайн-участник на сервер."
            }
        ]
    },
    "steam": {
        "label": "Steam",
        "emoji": "<:steam:1543647341129629756>",
        "banner": BANNER_STORE_STEAM,
        "description": "Пополнение баланса Steam.",
        "products": [
            {
                "name": "Пополнение баланса",
                "price": "1 руб. = 1.02 руб. на баланс",
                "description": "Курс пополнения Steam-кошелька."
            }
        ]
    }
}

# Фиксированные custom_id для "старых" категорий — чтобы кнопки
# остались теми же самыми и все ранее отправленные сообщения продолжали работать.
CATEGORY_CUSTOM_IDS = {
    "ds": "btn_store_ds",
    "boost": "btn_store_boost",
    "steam": "btn_store_steam"
}


def _save_catalog_sync(data: dict) -> None:
    """Синхронно сохраняет каталог в файл (используется только внутри блокировки)."""
    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _ensure_catalog_file() -> None:
    """Создаёт catalog.json с данными по умолчанию, если файла ещё нет."""
    if not os.path.exists(CATALOG_FILE):
        _save_catalog_sync(DEFAULT_CATALOG)


def load_catalog() -> dict:
    """Загружает каталог из catalog.json. При отсутствии/повреждении файла — создаёт заново."""
    _ensure_catalog_file()
    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        _save_catalog_sync(DEFAULT_CATALOG)
        return json.loads(json.dumps(DEFAULT_CATALOG))


async def save_catalog(data: dict) -> None:
    """Асинхронно и безопасно сохраняет каталог (с блокировкой от гонок записи)."""
    async with _catalog_lock:
        _save_catalog_sync(data)


def build_product_fields(products: list) -> list:
    """
    Формирует список полей Embed (name, value) со списком товаров,
    разбивая длинный список на несколько полей, чтобы не превысить лимит
    Discord в 1024 символа на значение поля.
    """
    if not products:
        return [("🛍️ Товары", "Пока нет товаров в этой категории.")]

    fields = []
    chunk = ""
    part = 1
    for product in products:
        entry = (
            f"**{product.get('name', 'Без названия')}**\n"
            f"> 💰 Цена: {product.get('price', 'уточняйте')}\n"
            f"> 📝 {product.get('description', 'Без описания')}\n\n"
        )
        if len(chunk) + len(entry) > 1000:
            title = "🛍️ Товары" if part == 1 else f"🛍️ Товары ({part})"
            fields.append((title, chunk.strip()))
            chunk = ""
            part += 1
        chunk += entry

    if chunk:
        title = "🛍️ Товары" if part == 1 else f"🛍️ Товары ({part})"
        fields.append((title, chunk.strip()))

    return fields


# ==========================================
# 1. МОДАЛЬНЫЕ ОКНА (MODALS)
# ==========================================
class OrderModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Какой товар желаете приобрести?",
                placeholder="Например: Создание сервера + бот",
                custom_id="order_item",
                style=disnake.TextInputStyle.short,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Способ оплаты",
                placeholder="Звёзды / Рубли (СБП, Карта и т.д.)",
                custom_id="order_payment",
                style=disnake.TextInputStyle.short,
                max_length=50
            ),
            disnake.ui.TextInput(
                label="Комментарий к заказу / Детали",
                placeholder="Опишите ваши пожелания...",
                custom_id="order_details",
                style=disnake.TextInputStyle.paragraph,
                required=False
            )
        ]
        super().__init__(title="Оформление заказа", custom_id="modal_order", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        guild = inter.guild
        category = guild.get_channel(CATEGORY_TICKETS_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)

        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            inter.author: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if staff_role:
            overwrites[staff_role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"заказ-{inter.author.name}",
            category=category,
            overwrites=overwrites
        )

        item = inter.text_values["order_item"]
        payment = inter.text_values["order_payment"]
        details = inter.text_values["order_details"] or "Не указано"

        embed = disnake.Embed(
            title="🛒 Новый заказ!",
            description=f"Пользователь {inter.author.mention} создал заказ.",
            color=disnake.Color.green()
        )
        embed.add_field(name="📦 Товар:", value=f"```\n{item}\n```", inline=False)
        embed.add_field(name="💳 Способ оплаты:", value=f"```\n{payment}\n```", inline=False)
        embed.add_field(name="📝 Детали:", value=f"```\n{details}\n```", inline=False)

        view = CloseTicketView()
        await ticket_channel.send(
            content=f"{inter.author.mention} {staff_role.mention if staff_role else ''}",
            embed=embed,
            view=view
        )
        await inter.edit_original_message(content=f"✅ Ваш заказ успешно создан: {ticket_channel.mention}")


class SupportModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Причина обращения / Вопрос",
                placeholder="Опишите вашу проблему или вопрос...",
                custom_id="support_reason",
                style=disnake.TextInputStyle.paragraph,
                max_length=1000
            )
        ]
        super().__init__(title="Обращение в поддержку", custom_id="modal_support", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        guild = inter.guild
        category = guild.get_channel(CATEGORY_TICKETS_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)

        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            inter.author: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if staff_role:
            overwrites[staff_role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"тикет-{inter.author.name}",
            category=category,
            overwrites=overwrites
        )

        reason = inter.text_values["support_reason"]

        embed = disnake.Embed(
            title="🛠️ Новое обращение в поддержку",
            description=f"Пользователь {inter.author.mention} обратился за помощью.",
            color=disnake.Color.orange()
        )
        embed.add_field(name="❓ Причина обращения:", value=f"```\n{reason}\n```", inline=False)

        view = CloseTicketView()
        await ticket_channel.send(
            content=f"{inter.author.mention} {staff_role.mention if staff_role else ''}",
            embed=embed,
            view=view
        )
        await inter.edit_original_message(content=f"✅ Тикет поддержки создан: {ticket_channel.mention}")


class StaffModal(disnake.ui.Modal):
    def __init__(self, role_name: str):
        self.role_name = role_name
        components = [
            disnake.ui.TextInput(
                label="Ваше имя и возраст",
                placeholder="Александр, 17 лет",
                custom_id="staff_age",
                style=disnake.TextInputStyle.short
            ),
            disnake.ui.TextInput(
                label="Сколько времени готовы уделять?",
                placeholder="3-4 часа в день",
                custom_id="staff_time",
                style=disnake.TextInputStyle.short
            ),
            disnake.ui.TextInput(
                label="Имелся ли опыт на аналогичной должности?",
                placeholder="Опишите ваш опыт...",
                custom_id="staff_experience",
                style=disnake.TextInputStyle.paragraph
            )
        ]
        super().__init__(title=f"Анкета: {role_name}", custom_id="modal_staff", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        log_channel = inter.guild.get_channel(STAFF_LOG_CHANNEL_ID)

        embed = disnake.Embed(
            title=f"📥 Новая заявка на должность: {self.role_name}",
            color=disnake.Color.blue(),
            timestamp=inter.created_at
        )
        embed.set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        embed.add_field(name="👤 Кандидат:", value=inter.author.mention, inline=True)
        embed.add_field(name="🆔 ID:", value=f"`{inter.author.id}`", inline=True)
        embed.add_field(name="📌 Должность:", value=f"`{self.role_name}`", inline=False)
        embed.add_field(name="🔞 Имя и возраст:", value=inter.text_values["staff_age"], inline=False)
        embed.add_field(name="⏰ Актив:", value=inter.text_values["staff_time"], inline=False)
        embed.add_field(name="💼 Опыт:", value=inter.text_values["staff_experience"], inline=False)

        if log_channel:
            view = StaffReviewView(applicant_id=inter.author.id, role_name=self.role_name)
            await log_channel.send(embed=embed, view=view)

        await inter.edit_original_message(content="✅ Ваша заявка отправлена на рассмотрение!")


class StaffRejectModal(disnake.ui.Modal):
    def __init__(self, applicant: disnake.Member, role_name: str):
        self.applicant = applicant
        self.role_name = role_name
        components = [
            disnake.ui.TextInput(
                label="Причина отказа",
                placeholder="Например: Не подходите по требованиям",
                custom_id="reject_reason",
                style=disnake.TextInputStyle.paragraph,
                max_length=500
            )
        ]
        super().__init__(title="Отказ в заявке", custom_id="modal_staff_reject", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer()
        reason = inter.text_values["reject_reason"]

        embed = inter.message.embeds[0]
        embed.color = disnake.Color.red()
        embed.add_field(
            name="❌ Статус:",
            value=f"Отклонено администратором {inter.author.mention}\n**Причина:** {reason}",
            inline=False
        )

        view = disnake.ui.View.from_message(inter.message)
        for child in view.children:
            child.disabled = True

        await inter.edit_original_message(embed=embed, view=view)

        try:
            await self.applicant.send(
                f"❌ Ваша заявка на должность **{self.role_name}** была отклонена.\n**Причина:** {reason}"
            )
        except disnake.Forbidden:
            pass


# ------------------------------------------
# 1.1 МОДАЛЬНЫЕ ОКНА ДЛЯ УПРАВЛЕНИЯ МАГАЗИНОМ (/shop)
# ------------------------------------------
class CategorySettingsModal(disnake.ui.Modal):
    """Модалка редактирования параметров категории: название, эмодзи, описание, баннер."""

    def __init__(self, cat_id: str, cat_data: dict):
        self.cat_id = cat_id
        components = [
            disnake.ui.TextInput(
                label="Название кнопки категории",
                custom_id="cat_label",
                style=disnake.TextInputStyle.short,
                value=cat_data.get("label", "") or "",
                max_length=80
            ),
            disnake.ui.TextInput(
                label="Эмодзи (например <:name:id> или 🔥)",
                custom_id="cat_emoji",
                style=disnake.TextInputStyle.short,
                value=cat_data.get("emoji", "") or "",
                required=False,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Описание категории (текст в Embed)",
                custom_id="cat_description",
                style=disnake.TextInputStyle.paragraph,
                value=cat_data.get("description", "") or "",
                required=False,
                max_length=1000
            ),
            disnake.ui.TextInput(
                label="Ссылка на баннер (URL картинки)",
                custom_id="cat_banner",
                style=disnake.TextInputStyle.short,
                value=cat_data.get("banner", "") or "",
                required=False,
                max_length=500
            )
        ]
        super().__init__(
            title=f"Настройка категории: {cat_id}"[:45],
            custom_id=f"modal_cat_settings_{cat_id}",
            components=components
        )

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        catalog = load_catalog()
        if self.cat_id not in catalog:
            await inter.edit_original_message(content="❌ Категория была удалена, действие отменено.")
            return

        catalog[self.cat_id]["label"] = inter.text_values["cat_label"]
        catalog[self.cat_id]["emoji"] = inter.text_values["cat_emoji"] or None
        catalog[self.cat_id]["description"] = inter.text_values["cat_description"]
        catalog[self.cat_id]["banner"] = inter.text_values["cat_banner"]
        await save_catalog(catalog)

        await inter.edit_original_message(
            content=f"✅ Категория **{catalog[self.cat_id]['label']}** обновлена.\n"
                    f"ℹ️ Чтобы изменения появились на витрине, повторно отправьте меню магазина через `/setup`."
        )


class AddProductModal(disnake.ui.Modal):
    """Модалка добавления нового товара в категорию."""

    def __init__(self, cat_id: str):
        self.cat_id = cat_id
        components = [
            disnake.ui.TextInput(
                label="Название товара",
                custom_id="p_name",
                style=disnake.TextInputStyle.short,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Цена",
                custom_id="p_price",
                style=disnake.TextInputStyle.short,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Описание",
                custom_id="p_desc",
                style=disnake.TextInputStyle.paragraph,
                required=False,
                max_length=300
            )
        ]
        super().__init__(title="Добавить товар", custom_id=f"modal_add_product_{cat_id}", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        catalog = load_catalog()
        if self.cat_id not in catalog:
            await inter.edit_original_message(content="❌ Категория не найдена.")
            return

        product = {
            "name": inter.text_values["p_name"],
            "price": inter.text_values["p_price"],
            "description": inter.text_values["p_desc"] or "Без описания"
        }
        catalog[self.cat_id].setdefault("products", []).append(product)
        await save_catalog(catalog)

        await inter.edit_original_message(
            content=f"✅ Товар **{product['name']}** добавлен в категорию **{catalog[self.cat_id].get('label', self.cat_id)}**."
        )


class EditProductModal(disnake.ui.Modal):
    """Модалка редактирования существующего товара по его индексу в списке категории."""

    def __init__(self, cat_id: str, index: int, product: dict):
        self.cat_id = cat_id
        self.index = index
        components = [
            disnake.ui.TextInput(
                label="Название товара",
                custom_id="p_name",
                style=disnake.TextInputStyle.short,
                value=product.get("name", ""),
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Цена",
                custom_id="p_price",
                style=disnake.TextInputStyle.short,
                value=product.get("price", ""),
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Описание",
                custom_id="p_desc",
                style=disnake.TextInputStyle.paragraph,
                value=product.get("description", ""),
                required=False,
                max_length=300
            )
        ]
        super().__init__(
            title="Редактировать товар",
            custom_id=f"modal_edit_product_{cat_id}_{index}",
            components=components
        )

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        catalog = load_catalog()
        products = catalog.get(self.cat_id, {}).get("products", [])

        if self.index >= len(products):
            await inter.edit_original_message(content="❌ Товар не найден (возможно, был удалён).")
            return

        products[self.index] = {
            "name": inter.text_values["p_name"],
            "price": inter.text_values["p_price"],
            "description": inter.text_values["p_desc"] or "Без описания"
        }
        await save_catalog(catalog)
        await inter.edit_original_message(content="✅ Товар успешно обновлён.")


class AddCategoryModal(disnake.ui.Modal):
    """Модалка создания новой категории каталога."""

    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Идентификатор категории (латиницей, без пробелов)",
                placeholder="Например: minecraft",
                custom_id="new_cat_id",
                style=disnake.TextInputStyle.short,
                max_length=40
            ),
            disnake.ui.TextInput(
                label="Название кнопки категории",
                custom_id="new_cat_label",
                style=disnake.TextInputStyle.short,
                max_length=80
            ),
            disnake.ui.TextInput(
                label="Эмодзи (необязательно)",
                custom_id="new_cat_emoji",
                style=disnake.TextInputStyle.short,
                required=False,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Описание категории",
                custom_id="new_cat_description",
                style=disnake.TextInputStyle.paragraph,
                required=False,
                max_length=1000
            )
        ]
        super().__init__(title="Новая категория", custom_id="modal_add_category", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        catalog = load_catalog()

        raw_id = inter.text_values["new_cat_id"].strip().lower()
        cat_id = "".join(ch for ch in raw_id if ch.isalnum() or ch == "_")

        if not cat_id:
            await inter.edit_original_message(content="❌ Некорректный идентификатор категории.")
            return
        if cat_id in catalog:
            await inter.edit_original_message(content="❌ Категория с таким идентификатором уже существует.")
            return

        catalog[cat_id] = {
            "label": inter.text_values["new_cat_label"],
            "emoji": inter.text_values["new_cat_emoji"] or None,
            "banner": "",
            "description": inter.text_values["new_cat_description"],
            "products": []
        }
        await save_catalog(catalog)

        await inter.edit_original_message(
            content=f"✅ Категория **{catalog[cat_id]['label']}** создана.\n"
                    f"ℹ️ Отправьте меню магазина заново через `/setup`, чтобы кнопка появилась на витрине."
        )


# ==========================================
# 2. ИНТЕРАКТИВНЫЕ КОМПОНЕНТЫ (VIEWS)
# ==========================================
class CloseTicketView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Закрыть тикет", style=disnake.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn")
    async def close_ticket(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("🔒 Канал будет удален через 5 секунд...")
        await asyncio.sleep(5)
        await inter.channel.delete()


class StaffReviewView(disnake.ui.View):
    def __init__(self, applicant_id: int, role_name: str):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
        self.role_name = role_name

    @disnake.ui.button(label="Одобрить", style=disnake.ButtonStyle.success, emoji="✅", custom_id="btn_staff_accept")
    async def accept(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        guild = inter.guild
        applicant = guild.get_member(self.applicant_id)
        if not applicant:
            await inter.response.send_message("❌ Кандидат не найден на сервере!", ephemeral=True)
            return

        staff_role = guild.get_role(STAFF_ROLE_ID)
        if staff_role:
            await applicant.add_roles(staff_role, reason=f"Заявка одобрена администратором {inter.author}")

        embed = inter.message.embeds[0]
        embed.color = disnake.Color.green()
        embed.add_field(name="✅ Статус:", value=f"Одобрено администратором {inter.author.mention}", inline=False)

        for child in self.children:
            child.disabled = True

        await inter.response.edit_message(embed=embed, view=self)

        try:
            await applicant.send(f"🎉 Поздравляем! Ваша заявка на должность **{self.role_name}** одобрена.")
        except disnake.Forbidden:
            pass

    @disnake.ui.button(label="Отклонить", style=disnake.ButtonStyle.danger, emoji="❌", custom_id="btn_staff_reject")
    async def reject(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        guild = inter.guild
        applicant = guild.get_member(self.applicant_id)
        if not applicant:
            await inter.response.send_message("❌ Кандидат не найден на сервере!", ephemeral=True)
            return
        await inter.response.send_modal(StaffRejectModal(applicant=applicant, role_name=self.role_name))


class OrderActionView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Сделать заказ",
        style=disnake.ButtonStyle.success,
        emoji="<:shop:1543647510634045490>",
        custom_id="btn_make_order"
    )
    async def make_order(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(OrderModal())


# ------------------------------------------
# 2.1 ВИТРИНА МАГАЗИНА — строится динамически из catalog.json
# ------------------------------------------
class CategoryButton(disnake.ui.Button):
    """Кнопка одной категории на витрине. custom_id сохраняется прежним для старых категорий."""

    def __init__(self, cat_id: str, cat_data: dict):
        custom_id = CATEGORY_CUSTOM_IDS.get(cat_id, f"btn_store_cat_{cat_id}")
        super().__init__(
            label=cat_data.get("label", cat_id),
            style=disnake.ButtonStyle.secondary,
            emoji=cat_data.get("emoji") or None,
            custom_id=custom_id
        )
        self.cat_id = cat_id

    async def callback(self, inter: disnake.MessageInteraction):
        catalog = load_catalog()
        cat_data = catalog.get(self.cat_id)

        if not cat_data:
            await inter.response.send_message("❌ Эта категория больше не существует.", ephemeral=True)
            return

        embed = disnake.Embed(
            title=f"{cat_data.get('label', self.cat_id)}",
            description=cat_data.get("description") or "\u200b",
            color=0x2b2d31
        )
        if cat_data.get("banner"):
            embed.set_image(url=cat_data["banner"])

        for name, value in build_product_fields(cat_data.get("products", [])):
            embed.add_field(name=name, value=value, inline=False)

        await inter.response.send_message(embed=embed, view=OrderActionView(), ephemeral=True)


class DynamicStoreView(disnake.ui.View):
    """Витрина магазина: одна кнопка на каждую категорию из catalog.json."""

    def __init__(self):
        super().__init__(timeout=None)
        catalog = load_catalog()
        for cat_id, cat_data in catalog.items():
            self.add_item(CategoryButton(cat_id, cat_data))


# ------------------------------------------
# 2.2 АДМИН-ПАНЕЛЬ МАГАЗИНА (/shop)
# ------------------------------------------
class ProductSelect(disnake.ui.StringSelect):
    def __init__(self, cat_id: str, options: list, action: str):
        placeholder = "Выберите товар для редактирования" if action == "edit" else "Выберите товар для удаления"
        super().__init__(
            placeholder=placeholder,
            options=options,
            custom_id=f"shop_admin_select_product_{action}_{cat_id}"
        )
        self.cat_id = cat_id
        self.action = action

    async def callback(self, inter: disnake.MessageInteraction):
        index = int(self.values[0])
        catalog = load_catalog()
        products = catalog.get(self.cat_id, {}).get("products", [])

        if index >= len(products):
            await inter.response.send_message("❌ Товар не найден (список мог измениться).", ephemeral=True)
            return

        if self.action == "edit":
            await inter.response.send_modal(EditProductModal(self.cat_id, index, products[index]))
        else:
            removed = products.pop(index)
            await save_catalog(catalog)
            await inter.response.edit_message(content=f"🗑️ Товар **{removed['name']}** удалён.", view=None)


class ProductSelectView(disnake.ui.View):
    def __init__(self, cat_id: str, products: list, action: str):
        super().__init__(timeout=180)
        options = [
            disnake.SelectOption(
                label=product.get("name", "Без названия")[:100],
                value=str(index),
                description=product.get("price", "")[:100] or None
            )
            for index, product in enumerate(products)
        ][:25]
        self.add_item(ProductSelect(cat_id, options, action))


class ShopCategoryActionView(disnake.ui.View):
    """Меню действий над выбранной категорией: настройки, добавить/редактировать/удалить товар."""

    def __init__(self, cat_id: str):
        super().__init__(timeout=180)
        self.cat_id = cat_id

    @disnake.ui.button(label="Настройки категории", style=disnake.ButtonStyle.primary, emoji="⚙️")
    async def edit_category(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        catalog = load_catalog()
        cat_data = catalog.get(self.cat_id)
        if not cat_data:
            await inter.response.send_message("❌ Категория не найдена.", ephemeral=True)
            return
        await inter.response.send_modal(CategorySettingsModal(self.cat_id, cat_data))

    @disnake.ui.button(label="Добавить товар", style=disnake.ButtonStyle.success, emoji="➕")
    async def add_product(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(AddProductModal(self.cat_id))

    @disnake.ui.button(label="Редактировать товар", style=disnake.ButtonStyle.secondary, emoji="✏️")
    async def edit_product(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        catalog = load_catalog()
        products = catalog.get(self.cat_id, {}).get("products", [])
        if not products:
            await inter.response.send_message("❌ В этой категории пока нет товаров.", ephemeral=True)
            return
        await inter.response.send_message(
            "Выберите товар для редактирования:",
            view=ProductSelectView(self.cat_id, products, action="edit"),
            ephemeral=True
        )

    @disnake.ui.button(label="Удалить товар", style=disnake.ButtonStyle.danger, emoji="🗑️")
    async def delete_product(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        catalog = load_catalog()
        products = catalog.get(self.cat_id, {}).get("products", [])
        if not products:
            await inter.response.send_message("❌ В этой категории пока нет товаров.", ephemeral=True)
            return
        await inter.response.send_message(
            "Выберите товар для удаления:",
            view=ProductSelectView(self.cat_id, products, action="delete"),
            ephemeral=True
        )


class ShopCategorySelect(disnake.ui.StringSelect):
    def __init__(self, options: list):
        super().__init__(
            placeholder="Выберите категорию для управления",
            options=options,
            custom_id="shop_admin_select_category"
        )

    async def callback(self, inter: disnake.MessageInteraction):
        cat_id = self.values[0]

        if cat_id == "__none__":
            await inter.response.send_message("❌ В каталоге пока нет категорий. Добавьте новую кнопкой ниже.", ephemeral=True)
            return

        catalog = load_catalog()
        cat_data = catalog.get(cat_id)
        if not cat_data:
            await inter.response.send_message("❌ Категория не найдена.", ephemeral=True)
            return

        embed = disnake.Embed(
            title=f"⚙️ Управление категорией: {cat_data.get('label', cat_id)}",
            description=f"Товаров в категории: **{len(cat_data.get('products', []))}**",
            color=0x2b2d31
        )
        await inter.response.send_message(embed=embed, view=ShopCategoryActionView(cat_id), ephemeral=True)


class AddCategoryButton(disnake.ui.Button):
    def __init__(self):
        super().__init__(label="Новая категория", style=disnake.ButtonStyle.success, emoji="➕", custom_id="shop_admin_add_category")

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.send_modal(AddCategoryModal())


class ShopCategorySelectView(disnake.ui.View):
    """Стартовое меню /shop: выбор категории для управления + создание новой категории."""

    def __init__(self):
        super().__init__(timeout=180)
        catalog = load_catalog()

        if catalog:
            options = [
                disnake.SelectOption(
                    label=data.get("label", cid)[:100],
                    value=cid,
                    description=f"Товаров: {len(data.get('products', []))}"
                )
                for cid, data in catalog.items()
            ]
        else:
            options = [disnake.SelectOption(label="Нет категорий", value="__none__")]

        self.add_item(ShopCategorySelect(options))
        self.add_item(AddCategoryButton())


class StaffSelectView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.string_select(
        placeholder="Выбери роль",
        custom_id="select_staff_role",
        options=[
            disnake.SelectOption(label="Trainee", value="Trainee", description="Стажер сервера", emoji="<:staff:1543647456196042932>"),
            disnake.SelectOption(label="Moderator", value="Moderator", description="Модератор чатов", emoji="<:staff:1543647456196042932>"),
            disnake.SelectOption(label="Support", value="Support", description="Агент поддержки", emoji="<:support:1543647293494796318>"),
        ]
    )
    async def select_callback(self, select: disnake.ui.StringSelect, inter: disnake.MessageInteraction):
        selected_role = select.values[0]
        await inter.response.send_modal(StaffModal(role_name=selected_role))


class SupportView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Открыть тикет", style=disnake.ButtonStyle.primary, emoji="<:support:1543647293494796318>", custom_id="btn_open_support")
    async def open_support(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(SupportModal())


# ==========================================
# 3. SLASH-КОМАНДА /SETUP (Только для Админов)
# ==========================================
@bot.slash_command(
    name="setup",
    description="Настройка и отправка системных меню (Доступно только администраторам)",
    default_member_permissions=disnake.Permissions(administrator=True)
)
@commands.has_permissions(administrator=True)
async def setup(
    inter: disnake.ApplicationCommandInteraction,
    menu_type: str = commands.Param(
        name="меню",
        description="Выберите какое меню нужно отправить в этот канал",
        choices={
            "Витрина / Магазин": "store",
            "Набор в Стафф": "staff",
            "Поддержка": "support"
        }
    )
):
    if menu_type == "store":
        catalog = load_catalog()

        lines = []
        for cid, data in catalog.items():
            emoji = data.get("emoji") or ""
            label = data.get("label", cid)
            desc = data.get("description") or ""
            lines.append(f"• {emoji} **{label}** — {desc}".strip())

        description = (
            "Выберите интересующую вас категорию и воспользуйтесь интерактивной кнопкой ниже, "
            "чтобы ознакомиться с ценами.\n\n" + "\n".join(lines)
        )

        embed = disnake.Embed(
            title="👋 Приветствуем в магазине!",
            description=description,
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_STORE_MAIN)

        await inter.channel.send(embed=embed, view=DynamicStoreView())
        await inter.response.send_message("✅ Меню магазина успешно отправлено!", ephemeral=True)

    elif menu_type == "staff":
        embed = disnake.Embed(
            title="Набор в команду",
            description="Станьте частью команды сервера и развивайтесь вместе с нами.\n"
                        "Выберите должность в меню ниже, чтобы заполнить анкету.\n\n"
                        "**Что от вас требуется:**\n"
                        "✦ • Возраст 16+\n"
                        "✧ • Минимальный актив в день: 2 часа\n"
                        "✦ • Грамотная письменная / устная речь\n"
                        "👑 • Желание развиваться и помогать участникам сервера\n\n"
                        "**Что вы получите от нас:**\n"
                        "✧ • Дружелюбный состав\n"
                        "✦ • Опыт в данной сфере\n"
                        "✧ • Понятная и прозрачная система повышений\n"
                        "👑 • Оплата труда / бонусы",
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_STAFF)
        embed.set_footer(text="Recruitment System")

        await inter.channel.send(embed=embed, view=StaffSelectView())
        await inter.response.send_message("✅ Меню набора успешно отправлено!", ephemeral=True)

    elif menu_type == "support":
        embed = disnake.Embed(
            title="🎧 Центр Поддержки",
            description="Возникли вопросы или проблемы? Нажмите кнопку ниже, чтобы связаться с администрацией.",
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_SUPPORT)

        await inter.channel.send(embed=embed, view=SupportView())
        await inter.response.send_message("✅ Меню поддержки успешно отправлено!", ephemeral=True)


# ==========================================
# 3.1 SLASH-КОМАНДА /SHOP (Управление товарами, только для Админов)
# ==========================================
@bot.slash_command(
    name="shop",
    description="Управление категориями и товарами магазина (Доступно только администраторам)",
    default_member_permissions=disnake.Permissions(administrator=True)
)
@commands.has_permissions(administrator=True)
async def shop(inter: disnake.ApplicationCommandInteraction):
    catalog = load_catalog()
    embed = disnake.Embed(
        title="🛠️ Управление магазином",
        description=(
            f"Всего категорий: **{len(catalog)}**\n"
            "Выберите категорию ниже, чтобы изменить её оформление или список товаров, "
            "либо создайте новую категорию."
        ),
        color=0x2b2d31
    )
    await inter.response.send_message(embed=embed, view=ShopCategorySelectView(), ephemeral=True)


# ==========================================
# 4. ГОЛОСОВОЙ КАНАЛ-СЧЁТЧИК УЧАСТНИКОВ
# ==========================================
# Discord ограничивает количество переименований одного канала примерно
# двумя изменениями за 10 минут. Чтобы не словить rate-limit при частом
# входе/выходе участников, обновление названия канала происходит не сразу,
# а по фоновому таймеру (раз в 10 минут), и только если состав менялся.
_counter_dirty = False


def _mark_counter_dirty():
    global _counter_dirty
    _counter_dirty = True


async def _apply_counter_update():
    """Ставит актуальное количество участников в название канала-счётчика."""
    global _counter_dirty

    if not COUNTER_CHANNEL_ID:
        return

    for guild in bot.guilds:
        channel = guild.get_channel(COUNTER_CHANNEL_ID)
        if channel is None:
            continue

        new_name = f"👥 Участников: {guild.member_count}"
        if channel.name == new_name:
            continue

        try:
            await channel.edit(name=new_name)
        except disnake.HTTPException as error:
            # Например, попали в rate-limit или не хватает прав — не роняем бота.
            print(f"⚠️ Не удалось обновить канал-счётчик участников: {error}")

    _counter_dirty = False


@tasks.loop(minutes=10)
async def update_counter_loop():
    if _counter_dirty:
        await _apply_counter_update()


@update_counter_loop.before_loop
async def before_update_counter_loop():
    await bot.wait_until_ready()


@bot.event
async def on_member_join(member: disnake.Member):
    _mark_counter_dirty()


@bot.event
async def on_member_remove(member: disnake.Member):
    _mark_counter_dirty()


# ==========================================
# 5. ЗАПУСК БОТА (BotHost.ru / Переменная TOKEN)
# ==========================================
@bot.event
async def on_ready():
    bot.add_view(DynamicStoreView())
    bot.add_view(OrderActionView())
    bot.add_view(StaffSelectView())
    bot.add_view(SupportView())
    bot.add_view(CloseTicketView())

    # Обновляем счётчик участников сразу при запуске, затем — по фоновому таймеру.
    _mark_counter_dirty()
    if not update_counter_loop.is_running():
        update_counter_loop.start()

    print(f"Бот {bot.user} успешно запущен!")


TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ Ошибка: Переменная окружения TOKEN не найдена! Укажите ее в панели хостинга.")
else:
    bot.run(TOKEN)
