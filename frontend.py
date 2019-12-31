from kivy.app import App
from mybackend import MyBackend
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ObjectProperty


class MyGrid(GridLayout):
    # location textbox
    tb_location = ObjectProperty(None)
    # location time spent textbox
    tb_spent: ObjectProperty(None)
    # location number of recommendation textbox
    tb_rec_num: ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MyGrid, self).__init__()
        # extracting model if exist
        self.model = kwargs.get('model', None)

    #Button EventHandler
    def get_recommendation(self):
        # input validation
        def validate(location, time, num):
            try:
                int(time)
            except Exception:
                return False, 'time spent must be an integer and greater then 0'
            try:
                int(num)
            except Exception:
                return False, 'number of result must be an integer and greater then 0'
            try:
                if len(location) == 0:
                    raise Exception('Location has not been set')
                elif (int(time) <= 0):
                    raise Exception('time spent must be an integer and greater then 0')
                elif (int(num) <= 0):
                    raise Exception('number of result must be an integer and greater then 0')
            except Exception as e:
                return False, e
            return True, None

        (valid, message) = validate(self.tb_location.text, self.tb_spent.text, self.tb_rec_num.text)
        title = ''
        if valid:
            title = 'Recommendation Location'
            lst_recommendation = self.model.get_recommendations(self.tb_location.text, int(self.tb_spent.text),
                                                                int(self.tb_rec_num.text))
            if (len(lst_recommendation) == 0):
                message = 'The start location is not exists'
            else:
                message = 'We recommend you to travel: \n%s' % ('\n'.join(lst_recommendation))
        else:
            title = 'Error'

        #Empty TextBoxes
        self.tb_location.text = ""
        self.tb_spent.text = ""
        self.tb_rec_num.text = ""

        Popup(title=title, size_hint=(None, None), size=(400, 400),
              content=Label(text=str(message), halign='center')).open()



class MyApp(App):
    def __init__(self):
        App.__init__(self)

    def build(self):
        return MyGrid(model=MyBackend())

if __name__=='__main__':
    app = MyApp()
    app.run()
