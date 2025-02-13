from quart import Quart, request, jsonify

dev = False
if dev:
    from GameCategories import GameCategories
    from BaseballData import BaseballData
else:
    from server.GameCategories import GameCategories
    from server.BaseballData import BaseballData
import datetime

app = Quart(__name__)

@app.after_request
async def after_request(response):
    if dev:
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    else:
        response.headers["Access-Control-Allow-Origin"] = "https://www.infiniteimmaculategrid.com"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

@app.route("/get_new_grid", methods=["GET"])
async def get_new_grid():
    categories = GameCategories()
    return jsonify(categories.get_grid())

@app.route("/search_players", methods=["GET"])
async def search_players():
    query = request.args.get("name")
    players = await BaseballData.search_players(query)
    data = players
    if len(data) > 0:
        if len(data) > 5:
            data = data[:5]
        players = []
        for x in range(len(data)):
            start = ''
            end = ''
            try:
                if data[x]['active']:
                    start = data[x]['mlbDebutDate'][:4]
                    end = datetime.datetime.now().year
                else:
                    start = data[x]['mlbDebutDate'][:4]
                    end = data[x]['lastPlayedDate'][:4]
                players.append(data[x]["fullName"] + f" | ({start}-{end})")
            except KeyError:
                players.append(data[x]["fullName"])
        return jsonify(players)
    return jsonify([])

@app.route("/validate_player", methods=["GET"])
async def validate_player():
    query = request.args.get("name")
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")
    players = await BaseballData.search_players(query)
    player = ''
    for x in range(len(players)):
        if players[x]["fullName"] == query:
            player = players[x]
            break
    teams = BaseballData.get_player_teams(player)
    if teams:
        if team1 in teams and team2 in teams:
            picture = BaseballData.get_player_picture(player)
            name = player["fullName"]
            return jsonify({"picture": picture, "name": name})
    # return nothing
    return jsonify({})

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)