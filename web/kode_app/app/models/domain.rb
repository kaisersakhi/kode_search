class Domain < ApplicationRecord
  self.table_name = "domain"
  has_many :urls
end
