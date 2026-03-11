-- Table: public.expenses

CREATE TABLE IF NOT EXISTS public.expenses
(
    id SERIAL NOT NULL,
    user_id bigint NOT NULL,
    completion_date timestamp without time zone NOT NULL DEFAULT now(),
    category character varying(200) NOT NULL,
    source character varying(255) NOT NULL,
    description text NOT NULL,
    total numeric(10,2) NOT NULL DEFAULT 0,
    CONSTRAINT expenses_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.expenses
    OWNER to lio_admin;
