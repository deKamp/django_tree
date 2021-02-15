function dateFilter(value, format="data") {
    // Фильтр для "русского" отображения даты
    const d = value.split('T',1)[0].split('-')
    return (d[2]+"."+d[1]+"."+d[0])
}

Vue.filter("date", dateFilter)

Vue.component("tree-item", {
    template: `
    <div class="row my-1 border rounded-sm">
        <div v-for="i in item.level" class="col-sm-1"></div>
        <div :class="[{[bootstrapBoldClass]:isFolder}, 'col-sm-3']">
            <span v-if="isFolder">
                <b-icon v-if="isOpen" class="mx-3" icon="folder-minus" scale="1.5" @click="toggle"></b-icon>
                <b-icon v-else class="mx-3" icon="folder-plus" scale="1.5" @click="toggle"></b-icon>
            </span>
            <b-icon v-else class="mx-3" icon="folder" variant="secondary" scale="1.5"></b-icon>
            [[ item.name ]] 
        </div>
        <div class="col-sm">
            <img :src="'/media/' + item.photo" width="50" height="50" class="img-thumbnail">
        </div>
        <div :class="[{[bootstrapBoldClass]:isFolder}, 'col-sm']">
                [[ item.position ]]
        </div>
        <div :class="[{[bootstrapBoldClass]:isFolder}, 'col-sm']">
            Заработная плата: [[ item.salary ]]
        </div>
        <div :class="[{[bootstrapBoldClass]:isFolder}, 'col-sm']">
            Дата приёма на работу: [[ item.start_date | date ]]
        </div>
        <div class="col-sm">
            <b-button variant="outline-info" size="sm" @click="$emit('changeclick', item)">
            <b-icon icon="pen" aria-hidden="true"></b-icon>
            Изменить</b-button>

            <b-button variant="outline-danger" size="sm" @click="$emit('deleteclick', item)">
            <b-icon icon="x-circle" aria-hidden="true"></b-icon>
            Удалить</b-button>
        </div>
        <div v-show="isOpen" v-if="isFolder">
            <tree-item
                v-for="(child, index) in item.children"
                :key="index"
                :item="child"
                @changeclick="$emit('changeclick', $event)"
                @deleteclick="$emit('deleteclick', $event)"
            ></tree-item>
        </div>
    </div>
    `,

    delimiters: ["[[", "]]"],
    props: {
        item: Object
    },
    data: function() {
        return {
            isOpen: false,
            bootstrapBoldClass: "fw-bold",
            serverUrl: JSON.parse(document.querySelector('#serverUrl').textContent)
        }
    },
    computed: {
        isFolder: function() {
            return (this.item.children.length)
        }
    },
    methods: {
        toggle: function() {
            if (!this.isOpen && !this.item.loaded) {
                // Если мы открываем ветку и объект не загружался ранее ... нужно его загрузить.
                // Механизм "lazy load" в действии
                this.item.loaded = !this.item.loaded
                axios.post(this.serverUrl + "get_node_childs/", {
                    "node_id": this.item.id
                },
                    {headers: {
                        "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value,
                        // Следующий хеадер нужен для правильной обработки django-функции "is_ajax" !!!
                        "X-Requested-With": "XMLHttpRequest"
                    }}, {
                        timeout: 1000
                    })
                        .then((response) => {
                            console.log("response", response.data.children)
                            this.item.children = response.data.children.slice()
                        })
                        .catch(function (error) {
                            console.log("error", error)
                        })
            }
            if (this.isFolder) {
                this.isOpen = !this.isOpen;
            }

        }
    }
})
