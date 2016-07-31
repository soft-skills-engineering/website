require "nokogiri"
require "date"


def fix_content(txt)
  durp = txt.split(/\n+/).map {|s| s.strip }
  durp.unshift("")
  durp.join("\n\n")
end

def fix_title(str)
  str = str.gsub(/(\d+)\./, "\\1:")
  "Episode #{str}"
end

def item_to_post(item)
  post = {
    title: fix_title(item.css("title").first.text),
    date: item.css("pubDate").first.text,
    guid: item.css("guid").first.text,
    duration: item.xpath("//itunes:duration").first.text,
    byte_size: item.css("enclosure").first["length"],
    file: item.css("enclosure").first["url"],
    content: fix_content(item.css("description").first.text),
  }
  update_post(post)
end

def update_post(post)
  date = DateTime::parse(post[:date])
  front_matter_date = date.strftime("%Y-%m-%d %H:%M:%S %z")
  post[:date] = front_matter_date

  file_name_date = date.strftime("%Y-%m-%d")
  post[:filename] = "#{file_name_date}-#{post[:title].downcase.split.join("-").gsub(/[^[[:alnum:]-]]/, "")[0, 80]}"
  post
end

def save_post(post)
  post_as_string = <<END
---
layout: post
title: "#{post[:title]}"
date: #{post[:date]}
guid: #{post[:guid]}
duration: "#{post[:duration]}"
length: #{post[:byte_size]}
file: "#{post[:file]}"
categories: episode
---

#{post[:content]}

END

  File.open("_posts/#{post[:filename]}.md", "w") { |f|
    f.write(post_as_string)
  }
end

doc = File.open("durp.xml") { |f| Nokogiri::XML(f) }

items = doc.css("item")

items.each do |item|
  post = item_to_post(item)
  save_post(post)
end
