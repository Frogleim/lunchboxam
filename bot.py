import logging
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, \
    CallbackContext
from telegram import Bot
from config import TOKEN, MAKE_ORDER, MAIN_MENU, CART, RESTART
from json_reader import drinks, hot_dishes, soups, salads
import gspread
import pandas as pd
import ast
import csv
from storage import save_orders_data


class Bots:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.updater = Updater(TOKEN)
        self.user_id = None
        self.my_bot = Bot(TOKEN)
        self.chat_id = None
        self.sa = gspread.service_account(filename='./lunchboxtelegram-a72d88f7f9dc.json')
        self.sh = self.sa.open('Menus')
        self.order_date = None
        self.username = None

        self.support_url = "https://t.me/+_nmBLd3yjkhhYTE6"
        self.orders = {}
        self.caption = None

    def join_group(self, update: Update, context: CallbackContext):
        """Entry action"""

        self.username = update.message.chat.first_name
        self.chat_id = update.effective_chat.id
        keyboard = [
            [
                InlineKeyboardButton("Պատվիրել այսօրվա համար", callback_data="Այսօր"),
            ],
            [InlineKeyboardButton("Պատվիրել վաղվա համար", callback_data="Վաղը")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Ընտրեք թվարկված մենյուից՝ ", reply_markup=reply_markup)

        return MAIN_MENU

    def hot_dish(self, update, context):
        print('Hot Dishes is selected')
        hot_dish_data = hot_dishes(sh=self.sh)
        for hot_dish_items in hot_dish_data:
            self.caption = f'{hot_dish_items[0]}, ԳԻն {hot_dish_items[1]}'
            hot_dishes_path = f'./images/Hot Dishes/{hot_dish_items[0]}.jpg'
            keyboard = [
                [
                    InlineKeyboardButton("Ավելացնել զամբյուղ", callback_data=f"{hot_dish_items[0], hot_dish_items[1]}"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.my_bot.send_photo(chat_id=update.effective_chat.id, photo=open(hot_dishes_path, 'rb'),
                                   caption=self.caption, reply_markup=reply_markup
                                   )

    def soups(self, update, context):
        soup_data = soups(sh=self.sh)
        for soups_items in soup_data:
            item = f'{soups_items[0]}, ԳԻն {soups_items[1]}'
            drinks_path = f'./images/Soups/{soups_items[0]}.jpg'
            keyboard = [
                [
                    InlineKeyboardButton("Ավելացնել զամբյուղ", callback_data=f"{soups_items[0], soups_items[1]}"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.my_bot.send_photo(chat_id=update.effective_chat.id, photo=open(drinks_path, 'rb'),
                                   caption=item, reply_markup=reply_markup
                                   )

    def salads(self, update, context):
        salads_data = salads(sh=self.sh)
        for salads_items in salads_data:
            item = f'{salads_items[0]}, ԳԻն {salads_items[1]}'
            drinks_path = f'./images/Salads/{salads_items[0]}.jpg'
            keyboard = [
                [
                    InlineKeyboardButton("Ավելացնել զամբյուղ", callback_data=f"{salads_items[0], salads_items[1]}"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.my_bot.send_photo(chat_id=update.effective_chat.id, photo=open(drinks_path, 'rb'),
                                   caption=item, reply_markup=reply_markup
                                   )

    def drinks(self, update, context):
        drinks_data = drinks(sh=self.sh)
        for drinks_items in drinks_data:
            item = f'{drinks_items[0]}, ԳԻն {drinks_items[1]}'
            drinks_path = f'./images/Drinks/{drinks_items[0]}.jpg'
            keyboard = [
                [
                    InlineKeyboardButton("Ավելացնել զամբյուղ",
                                         callback_data=f"{drinks_items[0], int(drinks_items[1])}"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.my_bot.send_photo(chat_id=update.effective_chat.id, photo=open(drinks_path, 'rb'),
                                   caption=item, reply_markup=reply_markup, timeout=100
                                   )

    def make_order(self, update: Update, context: CallbackContext):
        query = update.callback_query
        if query.data == 'hots':
            try:
                self.hot_dish(update, context)
            except Exception as e:
                print(e)
            return MAIN_MENU
        elif query.data == 'soup':
            try:
                self.soups(update, context)
            except Exception as e:
                print(e)
            return MAIN_MENU

        elif query.data == 'salad':
            try:
                self.salads(update, context)
            except Exception as e:
                print(e)
            return MAIN_MENU

        elif query.data == 'drink':
            try:
                self.drinks(update, context)
            except Exception as e:
                print(e)
            return MAIN_MENU

        elif query.data == 'cart':
            text = 'Կապ մեզ հետ՝'
            cart = self.get_orders(self.username)
            for items in cart:
                keyboard = [
                    [
                        InlineKeyboardButton("Ջնջել զամբյուղից", callback_data=f'remove-{items}'),
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=f'Ընտրեք թվարկված մենյուից՝ {items}',
                                             reply_markup=reply_markup
                                             )

                except Exception as e:
                    print(e)
            try:
                orders_sum = self.sum_calculating()
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f'Ընդհանուր պատվերի աարժեք՝ {orders_sum}',
                                         )
                continue_keyboard = [
                    [InlineKeyboardButton('Շարունակել', callback_data='continue')],
                ]
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=text + ' [' + self.support_url + '](' + self.support_url + ')', parse_mode=telegram.ParseMode.MARKDOWN,
                                         )
                continue_markup = InlineKeyboardMarkup(continue_keyboard)
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text='Վերադառնալ գլխավոր մենյու',
                                         reply_markup=continue_markup
                                         )
            except Exception as e:
                print(e)
            return CART
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Շնորհակալություն պատվերի համար \n'
                                          'Կրկին պատվիրելու համար մութքագրեք /start հրահանգը',
                                     )
            order = self.get_order()
            user_data = []
            users = {'user': order}
            user_data.append(users)
            df = pd.DataFrame(users)
            df.to_csv('User_Orders_for_check.csv')
            self.add_data(self.orders)
            save_orders_data(self.orders)
            return ConversationHandler.END

    def add_order(self, username, order_data):
        if username in self.orders:
            self.orders[username].append(order_data)
        else:
            self.orders[username] = [order_data]

    def get_order(self):
        print(self.orders)
        return self.orders

    def get_orders(self, username):
        print(self.orders)
        return self.orders.get(username)

    @staticmethod
    def add_data(data):
        with open('User_Orders_for_check.csv', 'a', newline='') as csv_file:
            # Create a writer object
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(data)

    def sum_calculating(self):
        order = self.get_order()
        user_data = []
        users = {'user': order}
        user_data.append(users)
        df = pd.DataFrame(users)
        df.to_csv('User_Orders_for_check.csv')
        file = pd.read_csv('./User_Orders_for_check.csv')
        list_form = None
        for items in file.user:
            print(items)
            list_form = ast.literal_eval(items)
        orders_sum = 0
        for orders in list_form[1:]:
            tuple_orders = ast.literal_eval(orders)
            orders_sum += int(tuple_orders[1])
            print(f'Total -> {orders_sum}')
        return orders_sum

    def main_menu(self, update: Update, context: CallbackContext):
        query = update.callback_query
        print('Query is: ', query.data)
        if query.data == '"(':
            tuple_form = ast.literal_eval(query.data)
            print('Transform is: ', tuple_form)
            self.add_order(self.username, tuple_form)
        else:
            self.add_order(self.username, query.data)
        print(self.get_order())
        keyboard = [
            [
                InlineKeyboardButton("Տաք ՈՒտեստ", callback_data="hots"),
            ],
            [InlineKeyboardButton("Ապուր", callback_data="soup")],
            [InlineKeyboardButton("Աղցան", callback_data="salad")],
            [InlineKeyboardButton("Ըմպելիք", callback_data="drink")],
            [InlineKeyboardButton("Իմ զամբյուղը", callback_data="cart")],
            [InlineKeyboardButton('Պատվիրել', callback_data='end')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Ընտրեք թվարկված մենյուից՝',
                                 reply_markup=reply_markup)
        return MAKE_ORDER

    def remove_item_from_cart(self, item):
        user_cart = self.get_order()
        user_cart.remove(item)
        print(user_cart)

    def restart(self, update: Update, context: CallbackContext):
        pass

    def cart(self, update: Update, context: CallbackContext):
        query = update.callback_query
        if 'remove' in query.data:
            self.remove_item_from_cart(query.data.split('-')[1])
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Զամբյուղից հեռացվեց՝ {query.data.split('-')[1]}")
            cart = self.get_orders(self.username)
            for items in cart:
                keyboard = [
                    [
                        InlineKeyboardButton("Ջնջել զամբյուղից", callback_data=f'remove-{items}'),
                    ],

                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f'Ձեր զամբյուղը՝ {items}',
                                         reply_markup=reply_markup
                                         )

            return MAKE_ORDER
        elif query.data == 'continue':
            print('Continuing')
            context.bot.send_message(chat_id=update.effective_chat.id, text='Շարոնակում ենք')
            keyboard = [
                [
                    InlineKeyboardButton("Տաք ուտեստներ", callback_data="hot"),
                ],
                [InlineKeyboardButton("Ապուր", callback_data="soup")],
                [InlineKeyboardButton("Աղցան", callback_data="salad")],
                [InlineKeyboardButton("Ըմպելիք", callback_data="drink")],
                [InlineKeyboardButton("Իմ զամբյուղը", callback_data="cart")],
                [InlineKeyboardButton('Պատվիրել', callback_data='end')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'Ընտրեք թվարկված մոնյւոից՝',
                                     reply_markup=reply_markup)
            return MAKE_ORDER

    def confirm_order(self, update: Update, context: CallbackContext):
        pass

    @staticmethod
    def cancel(update, _):
        update.message.reply_text(
            'You subscription was canceled'
        )
        return ConversationHandler.END

    def error(self, update, context):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    def run(self):
        """Start the bot."""
        dp = self.updater.dispatcher
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.join_group),
            ],
            states={
                RESTART: [CommandHandler('restart', self.restart)],
                MAKE_ORDER: [CallbackQueryHandler(self.make_order)],
                MAIN_MENU: [CallbackQueryHandler(self.main_menu)],
                CART: [CallbackQueryHandler(self.cart)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        dp.add_handler(conv_handler)
        dp.add_error_handler(self.error)
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    mybot = Bots()
    mybot.run()
