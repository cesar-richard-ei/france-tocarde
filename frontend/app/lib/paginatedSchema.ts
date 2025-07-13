import { z } from "zod";

export const GenericPaginatedSchema = z.object({
    count: z.number(),
    next: z.string().nullable(),
    previous: z.string().nullable(),
    results: z.array(z.any()),
});

export type GenericPaginated<T> = z.infer<typeof GenericPaginatedSchema>;

export const PaginatedSchema = <T>(schema: z.ZodType<T>) => GenericPaginatedSchema.extend({
    count: z.number(),
    next: z.string().nullable(),
    previous: z.string().nullable(),
    results: z.array(schema),
});
