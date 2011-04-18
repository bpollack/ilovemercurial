$(document).ready(function () {
  $('.tweet-text').each(function() {
    var tweetHtml = $(this).html();
    var newTweetHtml = tweetHtml.replace('#ilovemercurial', '<a class="hashtag" href="http://twitter.com/search/%23ilovemercurial">#ilovemercurial</a>')
    $(this).html(newTweetHtml);
  });
});