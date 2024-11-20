create table if not exists music_data (
	id serial primary key,
	music_name text not null,
	music_url text not null,
	user_id bigint not null
);