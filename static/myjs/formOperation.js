        // 获取form中的input对象
        function getInputsOnForm(formId){
            let form = document.getElementById(formId),
                inputs = form.getElementsByTagName('input'),
                ret = [];
            for(let i=0; i<inputs.length; i++)
                ret.push(inputs[i]);
            return ret;
        }

        // 获取单个input对象的键值对
        function getKvpOfInput(inputElem) {
            if(inputElem.type.toLowerCase() != 'radio' || inputElem.checked){
                return [inputElem.name, inputElem.value];
            }
        }

        function getKvpsOfForm(formId){
            let inputElemArray = getInputsOnForm(formId),
                kvp = {};
            for(let i=0; i<inputElemArray.length; i++){
                let tmp = getKvpOfInput(inputElemArray[i]);
                if(tmp){
                    kvp[tmp[0]] = tmp[1];
                }
            }
            return kvp;
        }