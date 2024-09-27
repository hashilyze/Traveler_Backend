from flask import Flask

app = Flask(__name__)


from BPR.BPR import recommend_restaurants

@app.get('/recommend/<int:id>')
def recommend(id):
    print(id)
    result = recommend_restaurants(id)
    return {
        'user': id,
        'restuarnts': result.tolist()
    }

app.run(debug=True)