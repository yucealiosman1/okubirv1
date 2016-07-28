function addToList(book_id) {
    var x = document.getElementById("status"+book_id).value;
    if(book_id != "-1"){
        document.location.href = '/add_book_to_user?book_id='+book_id+'&status='+x;
    }
}
