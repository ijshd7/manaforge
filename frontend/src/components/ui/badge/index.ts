import { cva, type VariantProps } from "class-variance-authority";

export { default as Badge } from "./Badge.vue";

export const badgeVariants = cva(
  "inline-flex items-center border-2 px-2 py-1 text-xs font-pixel transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-primary bg-primary text-primary-foreground hover:bg-primary/80",
        secondary:
          "border-secondary bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-destructive bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "border-primary text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export type BadgeVariants = VariantProps<typeof badgeVariants>;
