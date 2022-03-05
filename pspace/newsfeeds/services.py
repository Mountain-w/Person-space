from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService


class NewsFeedService:

    @classmethod
    def fanout_to_followers(cls, dynamic):
        # 错误的方法
        # 不可以将数据库操作放在 for 循环里面，效率会非常低
        # for follower in FriendshipService.get_followers(tweet.user):
        #     NewsFeed.objects.create(
        #         user=follower,
        #         tweet=tweet,
        #     )

        # 正确的方法：使用 bulk_create，会把 insert 语句合成一条
        followers = FriendshipService.get_followers(dynamic.user)
        newsfeeds = [
            NewsFeed(user_id=follower.id, dynamic=dynamic)
            for follower in followers
        ]
        newsfeeds.append((NewsFeed(user=dynamic.user, dynamic=dynamic)))
        NewsFeed.objects.bulk_create(newsfeeds)