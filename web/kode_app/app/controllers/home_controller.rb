require("transformers-rb")

class HomeController < ApplicationController
  @@model = Transformers.pipeline("embedding", "sentence-transformers/all-MiniLM-L6-v2")
  def index
    # render html: "hello world"
  end

  def search
    query = params[:query]
    @data = make_vespa_request(query)
  end

  def make_vespa_request(query)
    vespa_url = "http://localhost:8080/search/"
    embedding = @@model.(query).flatten

    uri = URI.parse(vespa_url)
    http = Net::HTTP.new(uri.host, uri.port)

    request = Net::HTTP::Post.new(uri)
    request.content_type = "application/json"

    request.body = {
      "yql" => "select * from kode_app where ({targetHits:10}nearestNeighbor(text_embedding, query_tensor))",
      "ranking" => "kode_app",
      "ranking.features.query(query_tensor)" => embedding
    }.to_json

    start_time = Time.now.to_f
    response = http.request(request)
    end_time = Time.now.to_f

    res = JSON.parse(response.body)

    data = {
      metadata: {
        query_time: (end_time - start_time) * 1000
      },
      items: []
    }

    res["root"]["children"].each do |item|
      fields = item["fields"]
      data[:items] << {
        title: fields["title"].split("-").first.gsub("_", " "),
        text: fields["text"],
        url: fields["url"]
      }
    end

    data
  end

  def indexed_domains
  end
end
