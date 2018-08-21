require 'sinatra'
require 'sinatra/json'
require "sinatra/reloader" if development?
require 'redis'

$redis = Redis.new

get '/' do
  haml :index
end

get '/arp' do
  keys = $redis.keys("arp:*#{params["q"]}*")
  @arp = []
  keys.each do |key|
    @arp << $redis.lrange(key, 0, -1).collect { |x| JSON.parse(x)}
  end
  json @arp.flatten!
end

get '/fdb' do
  keys = $redis.keys("fdb:*#{params["q"]}*")
  @fdb = []
  keys.each do |key|
    @fdb << $redis.lrange(key, 0, -1).collect { |x| JSON.parse(x)}
  end
  json @fdb.flatten!
end
