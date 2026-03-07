import { cva, type VariantProps } from "class-variance-authority";

export { default as Button } from "./Button.vue";

export const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border-2",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground border-primary hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_rgba(0,0,0,0.5)]",
        cta: "bg-accent text-accent-foreground border-accent font-pixel hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_rgba(0,0,0,0.5)]",
        destructive: "bg-destructive text-destructive-foreground border-destructive hover:bg-destructive/90",
        outline: "border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground border-secondary hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground border-transparent",
        link: "text-primary underline-offset-4 hover:underline border-transparent",
      },
      size: {
        default: "h-10 px-4 py-2 shadow-[4px_4px_0px_#4c1d95]",
        sm: "h-9 px-3 shadow-[2px_2px_0px_rgba(0,0,0,0.3)]",
        lg: "h-11 px-8 shadow-[4px_4px_0px_#4c1d95]",
        icon: "h-10 w-10 shadow-[4px_4px_0px_#4c1d95]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export type ButtonVariants = VariantProps<typeof buttonVariants>;
