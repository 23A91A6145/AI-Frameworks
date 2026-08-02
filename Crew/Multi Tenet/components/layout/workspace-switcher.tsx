"use client";

import { useState } from "react";
import { Building2, Check, Plus } from "lucide-react";

import { useSession } from "@/lib/session";
import { Button } from "@/components/ui/button";
import { Dropdown, DropdownItem } from "@/components/ui/dropdown";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Modal } from "@/components/ui/modal";
import { useToast } from "@/components/ui/toast";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";

export function WorkspaceSwitcher() {
  const { workspaces, activeWorkspace, setActiveWorkspace, createWorkspace, refresh } =
    useSession();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    if (!name.trim()) return;
    setSubmitting(true);
    try {
      await createWorkspace(name.trim(), slug.trim() || undefined);
      toast({ title: "Workspace created", variant: "success" });
      setOpen(false);
      setName("");
      setSlug("");
    } catch (error) {
      toast({
        title: "Could not create workspace",
        description: error instanceof Error ? error.message : "Something went wrong",
        variant: "error",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Dropdown
        trigger={
          <button className="flex cursor-pointer items-center gap-2 rounded-md border border-border bg-card px-3 py-1.5 text-sm font-medium shadow-sm transition hover:bg-muted">
            <Building2 className="h-4 w-4 text-primary" />
            <span className="max-w-[10rem] truncate">
              {activeWorkspace?.name ?? "Select workspace"}
            </span>
            <span className="text-muted-foreground">▾</span>
          </button>
        }
      >
        {(close) => (
          <>
            <p className="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Workspaces
            </p>
            {workspaces.map((workspace) => (
              <DropdownItem
                key={workspace.slug}
                active={activeWorkspace?.slug === workspace.slug}
                onClick={() => {
                  setActiveWorkspace(workspace);
                  refresh();
                  close();
                }}
              >
                <span className={cn("h-2 w-2 rounded-full bg-primary")} />
                {workspace.name}
                {activeWorkspace?.slug === workspace.slug && <Check className="h-3.5 w-3.5" />}
              </DropdownItem>
            ))}
            <div className="my-1 h-px bg-border" />
            <DropdownItem
              icon={<Plus className="h-4 w-4" />}
              onClick={() => {
                close();
                setOpen(true);
              }}
            >
              New workspace
            </DropdownItem>
          </>
        )}
      </Dropdown>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Create a new workspace"
        description="Every workspace gets its own isolated knowledge base and AI crew."
      >
        <div className="space-y-4">
          <div>
            <Label htmlFor="ws-name">Workspace name</Label>
            <Input
              id="ws-name"
              placeholder="Acme Support"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="ws-slug">Address (optional)</Label>
            <Input
              id="ws-slug"
              placeholder="acme-support"
              value={slug}
              onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, "-"))}
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Used in URLs. Auto-generated from the name if left empty.
            </p>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={submit} disabled={submitting || !name.trim()}>
              {submitting && <Spinner />}
              Create workspace
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
}
