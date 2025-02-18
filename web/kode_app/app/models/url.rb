class Url < ApplicationRecord
  self.table_name = "url"
  belongs_to :domain
end
