import vk_api
import pygsheets
import datetime

token = input('token: ')
comments = []
counts = []
likesData = [[], [], []]
commentsData = [[], []]
usersByLikes = {}
commentsByDay = {}
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
gc = pygsheets.authorize(client_secret='client_secret.json', local=True)

club = input('club short name or id: ')
club_id = vk.groups.getById(group_id=club)[0].get('id')
posts = vk.wall.get(owner_id=-club_id, count=100).get("items")
maxi = len(posts)

for i in range(0, maxi):
    post_id = posts[i].get("id")
    comments.append(vk.wall.getComments(owner_id=-club_id, post_id=post_id, count=100, extended=0, need_likes=1))
    counts.append(comments[i].get('count'))

for i in range(0, maxi):
    for j in range(0, len(comments[i].get('items'))):
        date = datetime.datetime.utcfromtimestamp(comments[i].get('items')[j].get("date")).strftime('%Y-%m-%d')
        if date in commentsByDay.keys():
            commentsByDay[date] += 1
        else:
            commentsByDay[date] = 1
        user_id = comments[i].get('items')[j].get("from_id")
        try:
            likes_count = comments[i].get('items')[j].get('likes').get('count')
        except:
            likes_count = 0
        if user_id in usersByLikes.keys():
            usersByLikes[user_id] += likes_count
        elif (comments[i].get('items')[j].get('likes') is not None) and (likes_count != 0) and (user_id > 0):
            usersByLikes[user_id] = likes_count

for user in usersByLikes.keys():
    likesData[0].append(user)
    likesData[1].append(
        vk.users.get(user_ids=user)[0].get('first_name') + " " + vk.users.get(user_id=user)[0].get('last_name'))
    likesData[2].append(usersByLikes[user])

new_matrix = [[likesData[j][i] for j in range(len(likesData))] for i in range(len(likesData[0]) - 1, -1, -1)]

sh = gc.open('Users by likes')
wks = sh.sheet1
wks.clear(start='A2')
wks.update_values('A2', new_matrix)

for date in commentsByDay.keys():
    commentsData[0].append(date)
    commentsData[1].append(commentsByDay[date])

new_matrix = [[commentsData[j][i] for j in range(len(commentsData))] for i in range(len(commentsData[0]) - 1, -1, -1)]

sh = gc.open('Comments by day')
wks = sh.sheet1
wks.clear(start='A2')
wks.update_values('A2', new_matrix)
