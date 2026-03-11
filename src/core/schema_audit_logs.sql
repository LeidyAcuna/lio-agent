-- Table: public.audit_logs

CREATE TABLE IF NOT EXISTS public.audit_logs
(
    id SERIAL NOT NULL,
    user_id bigint NOT NULL,
    fullname character varying(255),
    username character varying(255),
    chat_id bigint NOT NULL,
    message_text text NOT NULL,
    message_date timestamp without time zone NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT audit_logs_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.audit_logs
    OWNER to lio_admin;
