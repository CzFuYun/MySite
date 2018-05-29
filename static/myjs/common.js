function sortDict(dict, asc){
    let sort_key,
        new_dict = {};
    if(asc == null || asc){
        sort_key = Object.keys(dict).sort();
    }else{
        sort_key = Object.keys(dict).sort().reverse();
    }
    for(let i in sort_key){
        new_dict[sort_key[i]] = dict[sort_key[i]];
    }
    return new_dict;
}

function getKeyFromOneKvp(kvp){
    return Object.keys(kvp)[0];
}

function getValueFromOneKvp(kvp){
    return Object.values(kvp)[0];
}

// Array.prototype.insert = function (index, item) {
// //   this.splice(index, 0, item);
// // };