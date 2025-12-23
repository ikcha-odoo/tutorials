import { Component, useState } from "@odoo/owl";

export class Card extends Component {
    static template = "awesome_owl.Card";

    setup() {
        this.state = useState({
            title: "props.title",
            content: "props.content"
        });
    }
}