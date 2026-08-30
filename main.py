import os
import disnake
from disnake.ext import commands

intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# ID И НАСТРОЙКИ (Установлены твои ID)
# ==========================================
CATEGORY_TICKETS_ID = 1543635533375475833  # Категория, где будут создаваться тикеты
STAFF_LOG_CHANNEL_ID = 1543652454229352448 # Канал для заявок на стафф
STAFF_ROLE_ID = 1543621903539769344        # Роль персонала для доступа к тикетам

# Ссылки на баннеры
BANNER_STORE_MAIN = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648642152398948/Picsart_26-08-30_18-18-35-370.png?ex=6a95a253&is=6a9450d3&hm=7bae522765c81430084201be33cc556a08f3cbf75723ddd8cc19f1137698f03a&"
BANNER_STORE_DS = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648640847970384/Picsart_26-08-30_18-19-53-903.png?ex=6a95a253&is=6a9450d3&hm=1ac98b367169090139e9afebf7a49d5b1aca9cb9cda7c9adf1b9d4eb52aee5ef&"
BANNER_STORE_BOOST = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648640449642598/Picsart_26-08-30_18-20-30-349.png?ex=6a95a253&is=6a9450d3&hm=bf12d034845adf83143a09c3669e0d763e21c681519de3e903be7eda2f3107af&"
BANNER_STORE_STEAM = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648640118030376/Picsart_26-08-30_18-20-41-435.png?ex=6a95a253&is=6a9450d3&hm=e6443560d02e5c4b526feda64d7608ffd4824ff941c89b5a1c81f1a7b60a60b3&"
BANNER_STAFF = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648641636507699/Picsart_26-08-30_18-19-27-501.png?ex=6a95a253&is=6a9450d3&hm=f0a0d1dcb54b36a864465efc2563876cbfc8ff59ccabd83ae483786c98405d23&"
BANNER_SUPPORT = "https://cdn.discordapp.com/attachments/1543629832167104528/1543648641242239056/Picsart_26-08-30_18-19-41-401.png?ex=6a95a253&is=6a9450d3&hm=ba87b21f4140ae240fce10f22365842088c056c1dcadb0e806c874543df12091&"

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

class StoreView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Discord", style=disnake.ButtonStyle.secondary, emoji="<:discord:1543647404212093009>", custom_id="btn_store_ds")
    async def store_ds(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        embed = disnake.Embed(title="🌐 Товары — Discord", color=0x5865F2)
        embed.set_image(url=BANNER_STORE_DS)
        embed.add_field(
            name="Цены",
            value="```\n"
                  "Создание сервера                        | от 25⭐ / 40₽\n"
                  "Создание сервера + настройка ботов      | от 25⭐ / 40₽\n"
                  "Создание сервера с кастомным ботом       | от 50⭐ / 100₽\n"
                  "Создание ботов под задачи + хостинг     | от 50⭐ / 100₽\n"
                  "Хостинг вашего бота в дальнейшем        | 25⭐ / 50₽ мес.\n"
                  "```",
            inline=False
        )
        await inter.response.send_message(embed=embed, view=OrderActionView(), ephemeral=True)

    @disnake.ui.button(label="Накрутка DS", style=disnake.ButtonStyle.secondary, emoji="<:people:1543647540426055712>", custom_id="btn_store_boost")
    async def store_boost(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        embed = disnake.Embed(title="🚀 Накрутка Discord", color=0x5865F2)
        embed.set_image(url=BANNER_STORE_BOOST)
        embed.add_field(
            name="Цены (Заказ от 50 участников)",
            value="```\n"
                  "1 Оффлайн участник — 0.25₽\n"
                  "1 Онлайн участник  — 0.50₽\n"
                  "```",
            inline=False
        )
        await inter.response.send_message(embed=embed, view=OrderActionView(), ephemeral=True)

    @disnake.ui.button(label="Steam", style=disnake.ButtonStyle.secondary, emoji="<:steam:1543647341129629756>", custom_id="btn_store_steam")
    async def store_steam(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        embed = disnake.Embed(title="🎮 Пополнение Steam", color=0x1b2838)
        embed.set_image(url=BANNER_STORE_STEAM)
        embed.add_field(
            name="Курс пополнения",
            value="```\n1 Рубль = 1.02 Рубля на баланс\n```",
            inline=False
        )
        await inter.response.send_message(embed=embed, view=OrderActionView(), ephemeral=True)

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
        embed = disnake.Embed(
            title="👋 Приветствуем в магазине!",
            description="Выберите интересующую вас категорию и воспользуйтесь интерактивной кнопкой ниже, чтобы ознакомиться с ценами.\n\n"
                        "• <:discord:1543647404212093009> **Discord** — услуги связанные с серверами и ботами.\n"
                        "• <:people:1543647540426055712> **Накрутка DS** — участники для вашего сервера.\n"
                        "• <:steam:1543647341129629756> **Steam** — пополнение баланса.",
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_STORE_MAIN)
        await inter.channel.send(embed=embed, view=StoreView())
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
# 4. ЗАПУСК БОТА (BotHost.ru / Переменная TOKEN)
# ==========================================

@bot.event
async def on_ready():
    bot.add_view(StoreView())
    bot.add_view(OrderActionView())
    bot.add_view(StaffSelectView())
    bot.add_view(SupportView())
    bot.add_view(CloseTicketView())
    print(f"Бот {bot.user} успешно запущен!")

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ Ошибка: Переменная окружения TOKEN не найдена! Укажите ее в панели хостинга.")
else:
    bot.run(TOKEN)