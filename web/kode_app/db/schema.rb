# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.0].define(version: 0) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "domain", id: :serial, force: :cascade do |t|
    t.string "name", limit: 255, null: false
    t.index ["name"], name: "domain_name", unique: true
  end

  create_table "filequeue", id: :serial, force: :cascade do |t|
    t.integer "url_id", null: false
    t.string "path", limit: 255, null: false
    t.boolean "read", null: false
    t.index ["url_id"], name: "filequeue_url_id"
  end

  create_table "url", id: :serial, force: :cascade do |t|
    t.string "uri", limit: 255, null: false
    t.string "title", limit: 255, null: false
    t.string "html_file_path", limit: 255, null: false
    t.integer "domain_id", null: false
    t.datetime "downloaded_at", precision: nil, null: false
    t.index ["domain_id"], name: "url_domain_id"
    t.index ["title"], name: "url_title"
    t.index ["uri"], name: "url_uri", unique: true
  end

  add_foreign_key "filequeue", "url", name: "filequeue_url_id_fkey"
  add_foreign_key "url", "domain", name: "url_domain_id_fkey"
end
