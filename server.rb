require 'sinatra'
require "sinatra/reloader" if development?
require 'redis'

$redis = Redis.new

get '/' do
  @arp = $redis.lrange("arp_table", 0, -1).collect { |x| JSON.parse(x)}
  @fdb = $redis.lrange("fdb", 0, -1).collect { |x| JSON.parse(x)}
  haml :index
end
