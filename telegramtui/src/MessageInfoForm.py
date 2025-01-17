import curses
from telegramtui.src.telegramApi import client
from telegramtui.src import npyscreen
import textwrap
from datetime import timedelta
from telegramtui.src.config import get_config
import logging

logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)


class MessageInfoForm(npyscreen.ActionForm):

    def create(self):
        self.name = "Message Info"
        new_handlers = {
            # exit
            "^Q": self.exit_func,
            155: self.exit_func,
            curses.ascii.ESC: self.exit_func
        }
        self.add_handlers(new_handlers)

        config = get_config()
        self.timezone = int(config.get('other', 'timezone'))

        self.mess_id = self.add(npyscreen.TitleText, name="Message id:", editable=False)
        self.date = self.add(npyscreen.TitleText, name="Date:      ", editable=False)
        self.sender = self.add(npyscreen.TitleText, name="Sender:    ", editable=False)
        self.forward = self.add(npyscreen.TitleText, name="Fwd from:  ", editable=False)
        self.attachment = self.add(npyscreen.TitleText, name="Attachment:", editable=False)
        self.text = self.add(npyscreen.TitleMultiLine, name="Text:      ", max_height=5, scroll_exit=True)

    def update(self):
        current_user = self.parentApp.MainForm.chatBoxObj.value
        current_user_name = client.dialogs[current_user].name
        current_message = self.parentApp.MainForm.messageBoxObj.value
        messages = self.parentApp.MainForm.messageBoxObj.get_messages_info(current_user)
        current_id = messages[-current_message - 1].id

        message_info = client.get_message_by_id(current_user, current_id)
        prepared_text = self.prepare_message(message_info.message)

        self.current_user = current_user
        self.sender.value = current_user_name + " (id " + str(client.dialogs[current_user].entity.id) + ")"
        self.mess_id.value = current_id
        self.date.value = str(messages[-current_message - 1].date + (timedelta(self.timezone) // 24))
        self.attachment.value = self.prepare_media(message_info)
        self.forward.value = self.prepare_forward_messages(message_info)
        self.text.values = prepared_text
        self.text.max_height = len(prepared_text)
        self.display()

    def prepare_message(self, mess):
        y, x = self.useable_space()
        x -= 12
        out = []
        if mess is not None and mess != "":
            mess = mess.split("\n")
            for i in range(len(mess)):
                if len(mess[i]) > x - 10:
                    max_char = x - 10
                    arr = textwrap.wrap(mess[i], max_char)
                    for j in range(len(arr)):
                        out.append(arr[j])
                else:
                    out.append(mess[i])
        return out

    def prepare_media(self, obj):
        media = obj.media if hasattr(obj, 'media') else None
        if media is not None:
            if hasattr(media, 'photo'):
                out = "photo"
            elif hasattr(media, 'document'):
                try:
                    # print sticker like a emoji
                    if hasattr(media.document.attributes[1], 'stickerset'):
                        out = "Sticker"
                except:
                    out = "Document"
            else:
                out = "Unknown attachment"
        else:
            out = "None"

        return out

    def prepare_forward_messages(self, message):
        user_name = "None"
        fwd_from = message.fwd_from if hasattr(message, 'fwd_from') else None
        if fwd_from is not None:
            logger.debug('[message]')
            logger.debug(str(message))
            logger.debug(str(dir(message)))
            logger.debug('[fwd_from]')
            logger.debug(str(fwd_from))
            logger.debug(str(dir(fwd_from)))
            logger.debug('Messages:')
            logger.debug(str(client.messages))
        
            if fwd_from.from_id is not None:
                #logger.debug(str(dir(fwd_from)))
                #logger.debug(str(fwd_from.from_reader))
                #logger.debug(str(fwd_from.post_author))
                #logger.debug(str(fwd_from.to_dict()))
                sender = None
                #logger.debug(str(fwd_from.post_saved_from_msg_id))
                if hasattr(fwd_from, 'sender'):
                    sender = fwd_from.sender
                    user_name = '{} {} (id {})'.format(
                        sender.first_name, 
                        sender.last_name if hasattr(sender, 'first_name') and sender.first_name is not None else sender.last_name,
                        fwd_from.from_id
                    )
                    #user_name = sender.first_name + " " + sender.last_name if hasattr(sender, 'first_name') and \
                    #    sender.first_name is not None else sender.last_name
                    #user_name += " (id " + str(fwd_from.from_id) + ")"
                elif hasattr(fwd_from, 'saved_from_msg_id'):
                    user_name =  '(id {} saved from msg id {})'.format(fwd_from.from_id, fwd_from.saved_from_msg_id) 
                    # @TODO get author of the message
                    #user_name = 'TODO from m:' + str(fwd_from.saved_from_msg_id)
                                        
                   
            if fwd_from.channel_id is not None:
                logger.debug('Channel')
                logger.debug(str())
                if hasattr(fwd_from, 'channel'):
                    user_name = fwd_from.channel.title + " (id " + str(fwd_from.channel.id) + ")"
                elif hasattr(fwd_from, 'post_author'):
                    user_name = '{}'.format(fwd_from.post_author)
                    
        return user_name

    def on_ok(self):
        self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        self.parentApp.switchForm("MAIN")

    def exit_func(self, _input):
        exit(0)
