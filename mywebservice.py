from flask import Flask
from flask import jsonify
from flask import request
from mybackend import MyBackend


app = Flask(__name__)

#http://127.0.0.1:5000/?startlocation=Oakland+Ave&timeduration=5&k=5
@app.route('/',methods=['GET'])
def get_recommendation():
    def validate(location, time, num):
        try:
            int(time)
        except Exception:
            return (False, 'time spent must be an integer and greater then 0')
        try:
            int(num)
        except Exception:
            return (False, 'number of result must be an integer and greater then 0')
        try:
            if len(location) == 0:
                raise Exception('Location has not been set')
            elif (int(time) <= 0):
                raise Exception('time spent must be an integer and greater then 0')
            elif (int(num) <= 0):
                raise Exception('number of result must be an integer and greater then 0')
        except Exception as e:
            return (False, e)
        return (True, None)

    startlocation = request.args.get('startlocation', '')
    timeduration = request.args.get('timeduration', '')
    k = request.args.get('k', '')

    (valid, message) = validate(startlocation, timeduration, k)
    model = MyBackend()
    if valid:
        lst_recommendation = model.get_recommendations(startlocation, int(timeduration),int(k))
        # TODO decide what to show if we got less recomendation than 'self.tb_rec_num.text'
        if len(lst_recommendation) == 0:
            return jsonify('The start location is not exists')
        else:
            return jsonify(lst_recommendation)
    else:
        return jsonify('Error %s' %(message))

if __name__=='__main__':
    app.run(debug=True)
