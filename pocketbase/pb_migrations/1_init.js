/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
    const collection = new Collection({
        name: "assets",
        type: "base",
        listRule: "",
        viewRule: "",
        createRule: "",
        updateRule: "",
        deleteRule: "",
        fields: [
            {
                name: "type",
                type: "select",
                required: true,
                maxSelect: 1,
                values: ["image", "spritesheet", "sound", "lore"]
            },
            {
                name: "name",
                type: "text",
                required: true
            },
            {
                name: "prompt",
                type: "text",
                required: true
            },
            {
                name: "style",
                type: "text",
                required: false
            },
            {
                name: "file",
                type: "file",
                required: false,
                maxSelect: 1,
                maxSize: 52428800,
                mimeTypes: ["image/png", "image/jpeg", "image/webp", "audio/mpeg", "audio/mp3"]
            },
            {
                name: "content",
                type: "text",
                required: false
            },
            {
                name: "metadata",
                type: "json",
                required: false
            }
        ]
    });

    return app.save(collection);
}, (app) => {
    const collection = app.findCollectionByNameOrId("assets");
    return app.delete(collection);
});
