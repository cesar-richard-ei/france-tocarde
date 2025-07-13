import { z } from "zod";
import { PaginatedSchema } from "./paginatedSchema";

export const UserSchema = z.object({
    id: z.number(),
    last_login: z.string().nullable(),
    is_superuser: z.boolean(),
    is_staff: z.boolean(),
    is_active: z.boolean(),
    date_joined: z.string(),
    email: z.string(),
    last_name: z.string(),
    first_name: z.string(),
    address: z.string().nullable(),
    city: z.string().nullable(),
    zip_code: z.string().nullable(),
    country: z.string().nullable(),
    phone_number: z.string().nullable(),
    birth_date: z.string().nullable(),
    has_car: z.boolean(),
    car_seats: z.number(),
    can_host_peoples: z.boolean(),
    home_available_beds: z.number(),
    home_rules: z.string(),
    faluche_nickname: z.string().nullable(),
    faluche_status: z.string().nullable(),
});

export type User = z.infer<typeof UserSchema>;

export const PaginatedUsersSchema = PaginatedSchema(UserSchema);
export type PaginatedUsers = z.infer<typeof PaginatedUsersSchema>;
