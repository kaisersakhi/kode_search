require "net/http"

class HomeController < ApplicationController
  def index
    # render html: "hello world"
  end

  def search
    query = params[:query]
    @data = make_vespa_request(query)
  end

  def make_vespa_request(query)
    # TODO: update when dockerized
    vespa_url = "http://vespa:8080/search/"

    uri = URI.parse(vespa_url)
    http = Net::HTTP.new(uri.host, uri.port)

    request = Net::HTTP::Post.new(uri)
    request.content_type = "application/json"

    request.body = vector_search(query).to_json    
    
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

    res["root"]["children"]&.each do |item|
      fields = item["fields"]
      data[:items] << {
        title: fields["title"].split("-").first.gsub("_", " "),
        text: truncate_to_200_chars(fields["text"]),
        url: fields["url"]
      }
    end

    data
  end

  def indexed_domains
    @domains = Domain.joins(:urls).group(:name).select(:name, "COUNT(url.domain_id) AS url_count")
  end

  private

  def truncate_to_200_chars(str)
    new_str = str.length > 200 ? str[0..200] + "..." : str

    new_str.gsub!("<sep>", "")
    new_str.gsub!("</sep>", "")
    new_str.gsub!("<hi>", "<span class='text-white bg-yellow-700 rounded-sm px-1'>")
    new_str.gsub("</hi>", "</span>").html_safe
  end

  def vector_search(query)
    {
      "yql" =>"select title, text, url from kode_app WHERE ({targetHits:10}userInput(@user_query)) or ({targetHits:10}nearestNeighbor(text_embedding, e))",
      "input.query(e)" => "embed(e5, @user_query)",
      "user_query" => query
    }
  end
end
