function addToSaleForm(name, category, number, price) {
    event.preventDefault()
    // promise
    fetch('/api/add-saleform', {
        method: 'post',
        body: JSON.stringify({
            'name': name,
            'category': category,
            'number':number,
            'price': price
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        console.info(data)

    }).catch(function(err) {
        console.error(err)
    })
}


function pay_saleform() {
    if (confirm('Ban chac chan muon thanh toan khong?') == true) {
        fetch('/api/saleform_pay', {
            method: 'post'
        }).then(res => res.json()).then(data => {
            if (data.code == 200)
                location.reload()
        }).catch(err => console.error(err))
    }
}


function delete_saleform(id) {

}


