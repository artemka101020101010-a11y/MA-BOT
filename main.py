import os
import json
import copy

import disnake
from disnake.ext import commands, tasks

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True  # Обязательно для on_member_join / on_member_remove (счётчик участников)

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# ID И НАСТРОЙКИ (Установлены твои ID)
# ==========================================
CATEGORY_TICKETS_ID = 1543635533375475833  # Категория, где будут создаваться тикеты
STAFF_LOG_CHANNEL_ID = 1543652454229352448  # Канал для заявок на стафф
STAFF_ROLE_ID = 1543621903539769344  # Роль персонала для доступа к тикетам

# 🔊 Голосовой канал-счётчик участников сервера.
# Укажи сюда ID голосового канала, название которого бот будет
# автоматически обновлять вида "👥 Участников: 125".
COUNTER_CHANNEL_ID = 1550279189582848102  # <-- ЗАМЕНИ на реальный ID голосового канала

# Ссылки на баннеры
BANNER_STORE_MAIN = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648642152398948/Picsart_26-08-30_18-18-35-370.png?ex=6a95a253&is=6a9450d3&hm=7bae522765c81430084201be33cc556a08f3cbf75723ddd8cc19f1137698f03a&"
BANNER_STORE_DS = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648640847970384/Picsart_26-08-30_18-19-53-903.png?ex=6a95a253&is=6a9450d3&hm=1ac98b367169090139e9afebf7a49d5b1aca9cb9cda7c9adf1b9d4eb52aee5ef&"
BANNER_STORE_BOOST = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648640449642598/Picsart_26-08-30_18-20-30-349.png?ex=6a95a253&is=6a9450d3&hm=bf12d034845adf83143a09c3669e0d763e21c681519de3e903be7eda2f3107af&"
BANNER_STORE_STEAM = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648640118030376/Picsart_26-08-30_18-20-41-435.png?ex=6a95a253&is=6a9450d3&hm=e6443560d02e5c4b526feda64d7608ffd4824ff941c89b5a1c81f1a7b60a60b3&"
BANNER_STAFF = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648641636507699/Picsart_26-08-30_18-19-27-501.png?ex=6a95a253&is=6a9450d3&hm=f0a0d1dcb54b36a864465efc2563876cbfc8ff59ccabd83ae483786c98405d23&"
BANNER_SUPPORT = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648641242239056/Picsart_26-08-30_18-19-41-401.png?ex=6a95a253&is=6a9450d3&hm=ba87b21f4140ae240fce10f22365842088c056c1dcadb0e806c874543df12091&"

# ==========================================
# 0. КАТАЛОГ ТОВАРОВ (catalog.json)
# ==========================================
# Структура файла:
# {
#   "categories": {
#       "<cat_id>": {
#           "label": "Discord",                 -> название кнопки
#           "emoji": "<:discord:...>",          -> эмодзи кнопки (можно оставить "")
#           "banner": "https://...",            -> баннер категории
#           "description": "Текст описания",    -> вступительный текст в Embed категории
#           "products": [
#               {"name": "...", "price": "...", "description": "..."},
#               ...
#           ]
#       },
#       ...
#   }
# }
#
# custom_id кнопки категории собирается как f"btn_store_{cat_id}", поэтому
# для трёх изначальных категорий (ds / boost / steam) custom_id полностью
# совпадает со старыми "btn_store_ds", "btn_store_boost", "btn_store_steam" —
# ничего в уже существующих сообщениях не ломается.

CATALOG_FILE = "catalog.json"

DEFAULT_CATALOG = {
    "categories": {
        "ds": {
            "label": "Discord",
            "emoji": "<:discord:1543647404212093009>",
            "banner": BANNER_STORE_DS,
            "description": "🌐 **Товары — Discord**\nУслуги, связанные с серверами и ботами.",
            "products": [
                {"name": "Создание сервера", "price": "от 25⭐ / 40₽", "description": "Полная настройка сервера с нуля."},
                {"name": "Создание сервера + настройка ботов", "price": "от 25⭐ / 40₽", "description": "Сервер и базовая настройка ботов под ваши задачи."},
                {"name": "Создание сервера с кастомным ботом", "price": "от 50⭐ / 100₽", "description": "Сервер + уникальный бот под ваш проект."},
                {"name": "Создание ботов под задачи + хостинг", "price": "от 50⭐ / 100₽", "description": "Разработка бота и его размещение на хостинге."},
                {"name": "Хостинг вашего бота в дальнейшем", "price": "25⭐ / 50₽ мес.", "description": "Поддержка работы бота 24/7."},
            ],
        },
        "boost": {
            "label": "Накрутка DS",
            "emoji": "<:people:1543647540426055712>",
            "banner": BANNER_STORE_BOOST,
            "description": "🚀 **Накрутка Discord**\nУчастники для вашего сервера. Заказ от 50 участников.",
            "products": [
                {"name": "1 Оффлайн участник", "price": "0.25₽", "description": "Оффлайн-аккаунты, стабильно держатся на сервере."},
                {"name": "1 Онлайн участник", "price": "0.50₽", "description": "Онлайн-аккаунты, для живого вида сервера."},
            ],
        },
        "steam": {
            "label": "Steam",
            "emoji": "<:steam:1543647341129629756>",
            "banner": BANNER_STORE_STEAM,
            "description": "🎮 **Пополнение Steam**\nКурс пополнения: 1 Рубль = 1.02 Рубля на баланс.",
            "products": [
                {"name": "Пополнение баланса Steam", "price": "Курс 1 → 1.02", "description": "Оплата в рублях, зачисление на баланс Steam."},
            ],
        },
    }
}


def load_catalog() -> dict:
    """Загружает catalog.json. Если файла нет — создаёт его со стандартными категориями."""
    if not os.path.exists(CATALOG_FILE):
        save_catalog(DEFAULT_CATALOG)
        return copy.deepcopy(DEFAULT_CATALOG)
    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "categories" not in data:
                data["categories"] = {}
            return data
    except (json.JSONDecodeError, OSError):
        # Файл повреждён — не затираем его молча, а поднимаем дефолт в памяти
        return copy.deepcopy(DEFAULT_CATALOG)


def save_catalog(data: dict) -> None:
    """Сохраняет каталог в catalog.json."""
    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def format_products_field(products: list) -> str:
    """Красиво форматирует список товаров категории для Embed."""
    if not products:
        return "Пока нет доступных товаров."
    lines = []
    for p in products:
        name = p.get("name", "Без названия")
        price = p.get("price", "—")
        desc = p.get("description", "")
        block = f"**{name}** — `{price}`"
        if desc:
            block += f"\n{desc}"
        lines.append(block)
    text = "\n\n".join(lines)
    # Discord ограничивает значение поля Embed 1024 символами
    if len(text) > 1024:
        text = text[:1000] + "\n…"
    return text


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
        await ticket_channel.send(content=f"{inter.author.mention} {staff_role.mention if staff_role else ''}", embed=embed, view=view)
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
        await ticket_channel.send(content=f"{inter.author.mention} {staff_role.mention if staff_role else ''}", embed=embed, view=view)
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
        embed.add_field(name="❌ Статус:", value=f"Отклонено администратором {inter.author.mention}\n**Причина:** {reason}", inline=False)

        view = disnake.ui.View.from_message(inter.message)
        for child in view.children:
            child.disabled = True

        await inter.edit_original_message(embed=embed, view=view)

        try:
            await self.applicant.send(f"❌ Ваша заявка на должность **{self.role_name}** была отклонена.\n**Причина:** {reason}")
        except disnake.Forbidden:
            pass


# ------------------------------------------
# 1.1 МОДАЛЬНЫЕ ОКНА ДЛЯ УПРАВЛЕНИЯ МАГАЗИНОМ (/shop)
# ------------------------------------------

class CategoryEditModal(disnake.ui.Modal):
    """Редактирование параметров категории: название кнопки, эмодзи, текст, баннер."""

    def __init__(self, cat_id: str):
        self.cat_id = cat_id
        catalog = load_catalog()
        cat = catalog["categories"].get(cat_id, {})
        components = [
            disnake.ui.TextInput(
                label="Название кнопки",
                placeholder="Например: Discord",
                custom_id="cat_label",
                style=disnake.TextInputStyle.short,
                max_length=80,
                value=cat.get("label", "")
            ),
            disnake.ui.TextInput(
                label="Эмодзи кнопки (можно пусто)",
                placeholder="<:discord:1543647404212093009>",
                custom_id="cat_emoji",
                style=disnake.TextInputStyle.short,
                required=False,
                max_length=100,
                value=cat.get("emoji", "")
            ),
            disnake.ui.TextInput(
                label="Описание / текст категории",
                placeholder="Текст, который увидит пользователь в Embed",
                custom_id="cat_description",
                style=disnake.TextInputStyle.paragraph,
                required=False,
                max_length=1000,
                value=cat.get("description", "")
            ),
            disnake.ui.TextInput(
                label="Ссылка на баннер",
                placeholder="https://...",
                custom_id="cat_banner",
                style=disnake.TextInputStyle.short,
                required=False,
                max_length=300,
                value=cat.get("banner", "")
            ),
        ]
        super().__init__(title="Изменить категорию", custom_id=f"modal_cat_edit_{cat_id}", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        catalog = load_catalog()
        cat = catalog["categories"].setdefault(self.cat_id, {"products": []})
        cat["label"] = inter.text_values["cat_label"].strip() or cat.get("label", self.cat_id)
        cat["emoji"] = inter.text_values["cat_emoji"].strip()
        cat["description"] = inter.text_values["cat_description"].strip()
        cat["banner"] = inter.text_values["cat_banner"].strip()
        save_catalog(catalog)

        await inter.response.edit_message(
            content=f"✅ Категория **{cat['label']}** обновлена.\n"
                    f"⚠️ Чтобы новые название/эмодзи кнопки появились на витрине, "
                    f"повторно отправьте `/setup` → «Магазин» в нужный канал.",
            embed=build_category_manage_embed(self.cat_id, cat),
            view=ShopCategoryManageView(self.cat_id)
        )


class ProductAddModal(disnake.ui.Modal):
    """Добавление нового товара в категорию."""

    def __init__(self, cat_id: str):
        self.cat_id = cat_id
        components = [
            disnake.ui.TextInput(
                label="Название товара",
                placeholder="Например: Создание сервера",
                custom_id="prod_name",
                style=disnake.TextInputStyle.short,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Цена",
                placeholder="Например: от 25⭐ / 40₽",
                custom_id="prod_price",
                style=disnake.TextInputStyle.short,
                max_length=50
            ),
            disnake.ui.TextInput(
                label="Описание",
                placeholder="Краткое описание товара",
                custom_id="prod_description",
                style=disnake.TextInputStyle.paragraph,
                required=False,
                max_length=300
            ),
        ]
        super().__init__(title="Добавить товар", custom_id=f"modal_prod_add_{cat_id}", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        catalog = load_catalog()
        cat = catalog["categories"].setdefault(self.cat_id, {"products": []})
        cat.setdefault("products", []).append({
            "name": inter.text_values["prod_name"].strip(),
            "price": inter.text_values["prod_price"].strip(),
            "description": inter.text_values["prod_description"].strip(),
        })
        save_catalog(catalog)

        await inter.response.edit_message(
            content=f"✅ Товар **{inter.text_values['prod_name'].strip()}** добавлен в категорию **{cat.get('label', self.cat_id)}**.",
            embed=build_category_manage_embed(self.cat_id, cat),
            view=ShopCategoryManageView(self.cat_id)
        )


class ProductEditModal(disnake.ui.Modal):
    """Редактирование существующего товара по индексу в списке категории."""

    def __init__(self, cat_id: str, index: int):
        self.cat_id = cat_id
        self.index = index
        catalog = load_catalog()
        product = catalog["categories"].get(cat_id, {}).get("products", [])[index]
        components = [
            disnake.ui.TextInput(
                label="Название товара",
                custom_id="prod_name",
                style=disnake.TextInputStyle.short,
                max_length=100,
                value=product.get("name", "")
            ),
            disnake.ui.TextInput(
                label="Цена",
                custom_id="prod_price",
                style=disnake.TextInputStyle.short,
                max_length=50,
                value=product.get("price", "")
            ),
            disnake.ui.TextInput(
                label="Описание",
                custom_id="prod_description",
                style=disnake.TextInputStyle.paragraph,
                required=False,
                max_length=300,
                value=product.get("description", "")
            ),
        ]
        super().__init__(title="Редактировать товар", custom_id=f"modal_prod_edit_{cat_id}_{index}", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        catalog = load_catalog()
        cat = catalog["categories"].setdefault(self.cat_id, {"products": []})
        products = cat.setdefault("products", [])
        if self.index >= len(products):
            return await inter.response.send_message("❌ Этот товар уже был удалён.", ephemeral=True)

        products[self.index] = {
            "name": inter.text_values["prod_name"].strip(),
            "price": inter.text_values["prod_price"].strip(),
            "description": inter.text_values["prod_description"].strip(),
        }
        save_catalog(catalog)

        await inter.response.edit_message(
            content=f"✅ Товар обновлён в категории **{cat.get('label', self.cat_id)}**.",
            embed=build_category_manage_embed(self.cat_id, cat),
            view=ShopCategoryManageView(self.cat_id)
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
        await disnake.utils.sleep_until(disnake.utils.utcnow() + disnake.ext.tasks.datetime.timedelta(seconds=5))
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
            return await inter.response.send_message("❌ Кандидат не найден на сервере!", ephemeral=True)

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
            return await inter.response.send_message("❌ Кандидат не найден на сервере!", ephemeral=True)

        await inter.response.send_modal(StaffRejectModal(applicant=applicant, role_name=self.role_name))


class OrderActionView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Сделать заказ", style=disnake.ButtonStyle.success, emoji="<:shop:1543647510634045490>", custom_id="btn_make_order")
    async def make_order(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(OrderModal())


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


# ------------------------------------------
# 2.1 ВИТРИНА МАГАЗИНА (динамическая, на основе catalog.json)
# ------------------------------------------

class DynamicStoreView(disnake.ui.View):
    """
    Кнопки категорий магазина. Строится динамически из catalog.json,
    поэтому добавление/удаление/переименование категорий через /shop
    не требует правки кода. custom_id каждой кнопки — f"btn_store_{cat_id}",
    что для исходных категорий (ds/boost/steam) полностью совпадает
    со старыми custom_id и не ломает уже отправленные сообщения.
    """

    def __init__(self):
        super().__init__(timeout=None)
        self._build_buttons()

    def _build_buttons(self):
        self.clear_items()
        catalog = load_catalog()
        for cat_id, cat in catalog.get("categories", {}).items():
            emoji = cat.get("emoji") or None
            button = disnake.ui.Button(
                label=cat.get("label", cat_id),
                style=disnake.ButtonStyle.secondary,
                emoji=emoji,
                custom_id=f"btn_store_{cat_id}",
            )
            button.callback = self._make_callback(cat_id)
            self.add_item(button)

    @staticmethod
    def _make_callback(cat_id: str):
        async def callback(inter: disnake.MessageInteraction):
            catalog = load_catalog()
            cat = catalog.get("categories", {}).get(cat_id)
            if not cat:
                return await inter.response.send_message("❌ Эта категория больше не существует.", ephemeral=True)

            embed = disnake.Embed(
                title=f"{cat.get('label', cat_id)}",
                description=cat.get("description", ""),
                color=0x2b2d31
            )
            if cat.get("banner"):
                embed.set_image(url=cat["banner"])

            embed.add_field(name="🛍️ Товары", value=format_products_field(cat.get("products", [])), inline=False)

            # Под сообщением категории — кнопка "Сделать заказ" (не тронута, как и раньше)
            await inter.response.send_message(embed=embed, view=OrderActionView(), ephemeral=True)

        return callback


# ------------------------------------------
# 2.2 УПРАВЛЕНИЕ МАГАЗИНОМ (/shop) — Views для админов
# ------------------------------------------

def build_category_manage_embed(cat_id: str, cat: dict) -> disnake.Embed:
    embed = disnake.Embed(
        title=f"🗂️ Управление категорией: {cat.get('label', cat_id)}",
        color=0x2b2d31
    )
    embed.add_field(name="Эмодзи кнопки", value=cat.get("emoji") or "—", inline=True)
    embed.add_field(name="ID категории", value=f"`{cat_id}`", inline=True)
    embed.add_field(name="Баннер", value=cat.get("banner") or "—", inline=False)
    embed.add_field(name="Описание", value=cat.get("description") or "—", inline=False)

    products = cat.get("products", [])
    if products:
        lines = [f"`{i}.` **{p.get('name')}** — {p.get('price')}" for i, p in enumerate(products)]
        embed.add_field(name=f"Товары ({len(products)})", value="\n".join(lines)[:1024], inline=False)
    else:
        embed.add_field(name="Товары", value="Список пуст.", inline=False)

    return embed


class ShopCategorySelectView(disnake.ui.View):
    """Первый шаг /shop — выбор категории для управления."""

    def __init__(self, catalog: dict):
        super().__init__(timeout=180)
        options = [
            disnake.SelectOption(
                label=cat.get("label", cat_id),
                value=cat_id,
                description=f"Товаров: {len(cat.get('products', []))}",
                emoji=(cat.get("emoji") or None)
            )
            for cat_id, cat in catalog.get("categories", {}).items()
        ]
        if not options:
            options = [disnake.SelectOption(label="Нет категорий", value="__none__")]

        select = disnake.ui.StringSelect(
            placeholder="Выберите категорию для управления",
            custom_id="shop_select_category",
            options=options[:25]
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, inter: disnake.MessageInteraction):
        cat_id = inter.data["values"][0]
        if cat_id == "__none__":
            return await inter.response.send_message("❌ Категорий пока нет.", ephemeral=True)

        catalog = load_catalog()
        cat = catalog["categories"].get(cat_id)
        if not cat:
            return await inter.response.send_message("❌ Категория не найдена.", ephemeral=True)

        await inter.response.edit_message(
            content=None,
            embed=build_category_manage_embed(cat_id, cat),
            view=ShopCategoryManageView(cat_id)
        )


class ShopProductPickView(disnake.ui.View):
    """Выбор конкретного товара категории для редактирования или удаления."""

    def __init__(self, cat_id: str, action: str):
        super().__init__(timeout=180)
        self.cat_id = cat_id
        self.action = action  # "edit" или "delete"

        catalog = load_catalog()
        products = catalog["categories"].get(cat_id, {}).get("products", [])

        options = [
            disnake.SelectOption(label=p.get("name", f"Товар {i}")[:100], value=str(i), description=p.get("price", "")[:100])
            for i, p in enumerate(products)
        ]
        if not options:
            options = [disnake.SelectOption(label="Нет товаров", value="__none__")]

        select = disnake.ui.StringSelect(
            placeholder="Выберите товар",
            custom_id=f"shop_pick_product_{action}",
            options=options[:25]
        )
        select.callback = self.select_callback
        self.add_item(select)

        back_button = disnake.ui.Button(label="⬅️ Назад", style=disnake.ButtonStyle.secondary, custom_id=f"shop_back_{cat_id}")
        back_button.callback = self.back_callback
        self.add_item(back_button)

    async def back_callback(self, inter: disnake.MessageInteraction):
        catalog = load_catalog()
        cat = catalog["categories"].get(self.cat_id, {})
        await inter.response.edit_message(embed=build_category_manage_embed(self.cat_id, cat), view=ShopCategoryManageView(self.cat_id))

    async def select_callback(self, inter: disnake.MessageInteraction):
        value = inter.data["values"][0]
        if value == "__none__":
            return await inter.response.send_message("❌ В категории нет товаров.", ephemeral=True)

        index = int(value)

        if self.action == "edit":
            await inter.response.send_modal(ProductEditModal(self.cat_id, index))
        elif self.action == "delete":
            catalog = load_catalog()
            cat = catalog["categories"].setdefault(self.cat_id, {"products": []})
            products = cat.setdefault("products", [])
            if index >= len(products):
                return await inter.response.send_message("❌ Товар уже удалён.", ephemeral=True)

            removed = products.pop(index)
            save_catalog(catalog)

            await inter.response.edit_message(
                content=f"🗑️ Товар **{removed.get('name')}** удалён из категории **{cat.get('label', self.cat_id)}**.",
                embed=build_category_manage_embed(self.cat_id, cat),
                view=ShopCategoryManageView(self.cat_id)
            )


class ShopCategoryManageView(disnake.ui.View):
    """Основная панель управления выбранной категорией (для админов)."""

    def __init__(self, cat_id: str):
        super().__init__(timeout=180)
        self.cat_id = cat_id

    @disnake.ui.button(label="✏️ Изменить категорию", style=disnake.ButtonStyle.primary, row=0)
    async def edit_category(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(CategoryEditModal(self.cat_id))

    @disnake.ui.button(label="➕ Добавить товар", style=disnake.ButtonStyle.success, row=0)
    async def add_product(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(ProductAddModal(self.cat_id))

    @disnake.ui.button(label="📝 Редактировать товар", style=disnake.ButtonStyle.secondary, row=1)
    async def edit_product(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(view=ShopProductPickView(self.cat_id, action="edit"))

    @disnake.ui.button(label="🗑️ Удалить товар", style=disnake.ButtonStyle.danger, row=1)
    async def delete_product(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(view=ShopProductPickView(self.cat_id, action="delete"))

    @disnake.ui.button(label="⬅️ Ко всем категориям", style=disnake.ButtonStyle.secondary, row=2)
    async def back_to_categories(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        catalog = load_catalog()
        await inter.response.edit_message(
            content="🗂️ Выберите категорию для управления:",
            embed=None,
            view=ShopCategorySelectView(catalog)
        )


# ==========================================
# 3. SLASH-КОМАНДЫ
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

        # Список категорий формируется динамически из catalog.json
        lines = []
        for cat in catalog.get("categories", {}).values():
            emoji = cat.get("emoji", "")
            label = cat.get("label", "Категория")
            lines.append(f"• {emoji} **{label}**".strip())
        categories_text = "\n".join(lines) if lines else "Категории пока не добавлены."

        embed = disnake.Embed(
            title="👋 Приветствуем в магазине!",
            description="Выберите интересующую вас категорию и воспользуйтесь интерактивной кнопкой ниже, "
                        "чтобы ознакомиться с товарами и ценами.\n\n" + categories_text,
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


@bot.slash_command(
    name="shop",
    description="Управление категориями и товарами магазина (Доступно только администраторам)",
    default_member_permissions=disnake.Permissions(administrator=True)
)
@commands.has_permissions(administrator=True)
async def shop(inter: disnake.ApplicationCommandInteraction):
    catalog = load_catalog()
    await inter.response.send_message(
        "🗂️ Выберите категорию для управления:",
        view=ShopCategorySelectView(catalog),
        ephemeral=True
    )


@shop.sub_command(name="категория", description="Создать новую категорию товаров")
async def shop_add_category(
        inter: disnake.ApplicationCommandInteraction,
        id_категории: str = commands.Param(
            name="id",
            description="Короткий идентификатор латиницей без пробелов, например: hosting"
        ),
        название: str = commands.Param(description="Название кнопки категории")
):
    catalog = load_catalog()
    cat_id = id_категории.strip().lower().replace(" ", "_")

    if not cat_id.isalnum() and "_" not in cat_id:
        return await inter.response.send_message("❌ ID категории должен состоять из латинских букв, цифр и `_`.", ephemeral=True)

    if cat_id in catalog["categories"]:
        return await inter.response.send_message("❌ Категория с таким ID уже существует.", ephemeral=True)

    catalog["categories"][cat_id] = {
        "label": название.strip(),
        "emoji": "",
        "banner": "",
        "description": "",
        "products": []
    }
    save_catalog(catalog)

    await inter.response.send_message(
        f"✅ Категория **{название}** (`{cat_id}`) создана.\n"
        f"Используйте `/shop`, чтобы настроить эмодзи, баннер, описание и добавить товары.\n"
        f"⚠️ Не забудьте повторно отправить `/setup` → «Магазин», чтобы новая кнопка появилась на витрине.",
        ephemeral=True
    )


# ==========================================
# 4. СЧЁТЧИК УЧАСТНИКОВ (голосовой канал)
# ==========================================
# Discord ограничивает частоту переименования каналов (по факту — около
# 2 изменений имени за 10 минут на канал). Чтобы не словить рейт-лимит,
# бот не переименовывает канал сразу при каждом входе/выходе участника,
# а лишь выставляет флаг "нужно обновить" и раз в COUNTER_UPDATE_INTERVAL
# секунд проверяет его через фоновую задачу (tasks.loop).

COUNTER_UPDATE_INTERVAL = 600  # 10 минут — безопасный интервал обновления имени канала
_member_count_dirty = False


@tasks.loop(seconds=COUNTER_UPDATE_INTERVAL)
async def counter_channel_updater():
    global _member_count_dirty

    if not COUNTER_CHANNEL_ID:
        return
    if not _member_count_dirty:
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
        except disnake.HTTPException as e:
            # Например, попали в rate-limit или не хватает прав — не роняем бота
            print(f"⚠️ Не удалось обновить канал-счётчик участников: {e}")

    _member_count_dirty = False


@bot.event
async def on_member_join(member: disnake.Member):
    global _member_count_dirty
    _member_count_dirty = True


@bot.event
async def on_member_remove(member: disnake.Member):
    global _member_count_dirty
    _member_count_dirty = True


# ==========================================
# 5. ЗАПУСК БОТА (BotHost.ru / Переменная TOKEN)
# ==========================================

@bot.event
async def on_ready():
    # Убеждаемся, что catalog.json существует
    load_catalog()

    # Регистрируем персистентные View, чтобы кнопки работали после перезапуска бота
    bot.add_view(DynamicStoreView())
    bot.add_view(OrderActionView())
    bot.add_view(StaffSelectView())
    bot.add_view(SupportView())
    bot.add_view(CloseTicketView())

    # Запускаем фоновую задачу обновления канала-счётчика участников
    if not counter_channel_updater.is_running():
        counter_channel_updater.start()

    # Сразу актуализируем название канала-счётчика при старте бота (один запрос — лимит не страдает)
    if COUNTER_CHANNEL_ID:
        for guild in bot.guilds:
            channel = guild.get_channel(COUNTER_CHANNEL_ID)
            if channel:
                new_name = f"👥 Участников: {guild.member_count}"
                if channel.name != new_name:
                    try:
                        await channel.edit(name=new_name)
                    except disnake.HTTPException as e:
                        print(f"⚠️ Не удалось обновить канал-счётчик участников при старте: {e}")

    print(f"Бот {bot.user} успешно запущен!")


TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ Ошибка: Переменная окружения TOKEN не найдена! Укажите ее в панели хостинга.")
else:
    bot.run(TOKEN)
